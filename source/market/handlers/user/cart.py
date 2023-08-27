import logging

from source.config import MAIN_ADMIN
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from source.market.keyboards.inline.products_from_cart import product_markup, product_cb
from aiogram.utils.callback_data import CallbackData
from source.market.keyboards.default.markups import *
from aiogram.types.chat import ChatActions
from source.market.handlers.states import CheckoutState
from source.bot_init import dp, db, bot
from source.market.filters import IsUser, IsAdmin
from .menu import cart
from source.single_chat.start_handler import start_work
from source.market.keyboards.inline.categories import make_inline_keyboard
from source.market.keyboards.default.markups import make_reply_keyboard


@dp.message_handler(IsUser(), text=cart)
async def process_cart(message: Message, state: FSMContext):

    cart_data = db.fetchall(
        'SELECT * FROM cart WHERE cid=%s', (message.chat.id,))

    if len(cart_data) == 0:

        await message.answer('Ваша корзина пуста.')

    else:

        await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
        async with state.proxy() as data:
            data['products'] = {}

        order_cost = 0

        for _, idx, count_in_cart in cart_data:

            product = db.fetchone('SELECT * FROM products WHERE idx=%s', (idx,))

            if product == None:

                db.query('DELETE FROM cart WHERE idx=%s', (idx,))

            else:
                _, title, body, image, price, _ = product
                order_cost += price

                async with state.proxy() as data:
                    data['products'][idx] = [title, price, count_in_cart]

                markup = product_markup(idx, count_in_cart)
                text = f'<b>{title}</b>\n\n{body}\n\nЦена: {price}€.'

                await message.answer_photo(photo=image,
                                           caption=text,
                                           reply_markup=make_inline_keyboard(markup), parse_mode='HTML')

        if order_cost != 0:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add('📦 Оформить заказ')

            await message.answer('Перейти к оформлению?',
                                 reply_markup=make_reply_keyboard(markup))


@dp.callback_query_handler(IsUser(), product_cb.filter(action='count'))
@dp.callback_query_handler(IsUser(), product_cb.filter(action='increase'))
@dp.callback_query_handler(IsUser(), product_cb.filter(action='decrease'))
async def product_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):

    idx = callback_data['id']
    action = callback_data['action']

    if 'count' == action:

        async with state.proxy() as data:

            if 'products' not in data.keys():

                await process_cart(query.message, state)

            else:

                await query.answer('Количество - ' + data['products'][idx][2])

    else:

        async with state.proxy() as data:

            if 'products' not in data.keys():

                await process_cart(query.message, state)

            else:

                data['products'][idx][2] += 1 if 'increase' == action else -1
                count_in_cart = data['products'][idx][2]

                if count_in_cart == 0:

                    db.query('''DELETE FROM cart
                    WHERE cid = %s AND idx = %s''', (query.message.chat.id, idx))

                    await query.message.delete()
                else:

                    db.query('''UPDATE cart 
                    SET quantity = %s 
                    WHERE cid = %s AND idx = %s''', (count_in_cart, query.message.chat.id, idx))

                    await query.message.edit_reply_markup(make_inline_keyboard(product_markup(idx, count_in_cart)))


@dp.message_handler(IsUser(), text='📦 Оформить заказ')
async def process_checkout(message: Message, state: FSMContext):

    await CheckoutState.check_cart.set()
    await checkout(message, state)


async def checkout(message, state):
    answer = ''
    total_price = 0

    async with state.proxy() as data:

        for title, price, count_in_cart in data['products'].values():

            tp = count_in_cart * price
            answer += f'<b>{title}</b> * {count_in_cart}шт. = {tp}€\n'
            total_price += tp

    await message.answer(f'{answer}\nОбщая сумма заказа: {total_price}€.',
                        parse_mode='HTML', reply_markup=make_reply_keyboard(check_markup()))


@dp.message_handler(IsUser(), lambda message: message.text not in [all_right_message, back_message], state=CheckoutState.check_cart)
async def process_check_cart_invalid(message: Message):
    await message.reply('Такого варианта не было.')


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.check_cart)
async def process_check_cart_back(message: Message, state: FSMContext):
    await state.finish()
    await process_cart(message, state)


@dp.message_handler(IsUser(), text=all_right_message, state=CheckoutState.check_cart)
async def process_check_cart_all_right(message: Message, state: FSMContext):
    await CheckoutState.next()
    await message.answer('Укажите свое имя.',
                         reply_markup=make_reply_keyboard(back_markup()))


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.name)
async def process_name_back(message: Message, state: FSMContext):
    await CheckoutState.check_cart.set()
    await checkout(message, state)


@dp.message_handler(IsUser(), state=CheckoutState.name)
async def process_name(message: Message, state: FSMContext):

    async with state.proxy() as data:

        data['name'] = message.text

        if 'address' in data.keys():

            await confirm(message)
            await CheckoutState.confirm.set()

        else:

            await CheckoutState.next()
            await message.answer('Укажите свой адрес места жительства.',
                                 reply_markup=make_reply_keyboard(back_markup()))


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.address)
async def process_address_back(message: Message, state: FSMContext):

    async with state.proxy() as data:

        await message.answer('Изменить имя с <b>' + data['name'] + '</b>?',
                            parse_mode='HTML', reply_markup=make_reply_keyboard(back_markup()))

    await CheckoutState.name.set()


@dp.message_handler(IsUser(), state=CheckoutState.address)
async def process_address(message: Message, state: FSMContext):

    async with state.proxy() as data:
        data['address'] = message.text

    await confirm(message)
    await CheckoutState.next()


async def confirm(message):

    await message.answer('Убедитесь, что все правильно оформлено и подтвердите заказ.',
                         reply_markup=make_reply_keyboard(confirm_markup()))


@dp.message_handler(IsUser(), lambda message: message.text not in [confirm_message, back_message], state=CheckoutState.confirm)
async def process_confirm_invalid(message: Message):
    await message.reply('Такого варианта не было.')


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):

    await CheckoutState.address.set()

    async with state.proxy() as data:
        await message.answer('Изменить адрес с <b>' + data['address'] + '</b>?',
                            parse_mode='HTML', reply_markup=make_reply_keyboard(back_markup()))


@dp.message_handler(IsUser(), text=confirm_message, state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):

    enough_money = True
    markup = ReplyKeyboardRemove()

    if enough_money:

        logging.info('Deal was made.')

        async with state.proxy() as data:

            cid = message.chat.id
            products = [idx + '=' + str(quantity)
                        for idx, quantity in db.fetchall('''SELECT idx, quantity FROM cart
            WHERE cid=%s''', (cid,))]  # idx=quantity

            # Insert the order into the orders table and get the generated order_id
            db.query('INSERT INTO orders (cid, usr_name, usr_address, products) VALUES (%s, %s, %s, %s) RETURNING order_id',
                     (cid, data['name'], data['address'], ' '.join(products)))

            order_id = db.fetchone('SELECT order_id FROM orders WHERE cid = %s ORDER BY order_id DESC LIMIT 1', (cid,))[0]

            for product in products:
                product = product.split('=')
                count = product[1]
                tag = product[0]
                name = db.fetchall('''SELECT title FROM products WHERE idx=%s''', (tag,))
                await bot.send_message(chat_id=MAIN_ADMIN, text=f'Создан заказ:\nТовар: <b>{name[0][0]}</b>\nКоличество: <b>{count}</b>\nКуда: <b>{data["address"]}</b>\nИмя:  <b>{data["name"]}</b>')

            db.query('DELETE FROM cart WHERE cid=%s', (cid,))

            await message.answer(f'Ок! Ваш заказ с номером {order_id} в обработке!\nИмя: <b>{data["name"]}</b>\nАдрес: <b>{data["address"]}</b>',
                    parse_mode='HTML', reply_markup=markup)
            await start_work(message)
            await state.finish()
            return
    else:

        await message.answer('У вас недостаточно денег на счете. Пополните баланс!',
                             reply_markup=markup)

    await state.finish()
