import logging
from aiogram.types import Message, CallbackQuery
from source.market.keyboards.inline.categories import categories_markup, category_cb
from source.market.keyboards.inline.products_from_catalog import product_markup, product_cb
from aiogram.utils.callback_data import CallbackData
from aiogram.types.chat import ChatActions
from source.bot_init import dp, db, bot
from .menu import catalog
from source.market.filters import IsUser


@dp.message_handler(IsUser(), text=catalog)
async def process_catalog(message: Message):
    await message.answer('Выберите раздел, чтобы вывести список товаров:',
                         reply_markup=categories_markup())


@dp.callback_query_handler(IsUser(), category_cb.filter(action='view'))
async def category_callback_handler(query: CallbackQuery, callback_data: dict):

    products = db.fetchall('''SELECT * FROM products product
    WHERE product.tag = (SELECT title FROM categories WHERE idx=%s) 
    AND product.idx NOT IN (SELECT idx FROM cart WHERE cid = %s)''',
                           (callback_data['id'], query.message.chat.id))

    await query.answer('Все доступные товары.')
    await show_products(query.message, products)


@dp.callback_query_handler(IsUser(), product_cb.filter(action='add'))
async def add_product_callback_handler(query: CallbackQuery, callback_data: dict):

    db.query('INSERT INTO cart VALUES (%s, %s, 1)',
             (query.message.chat.id, callback_data['id']))

    await query.answer('Товар добавлен в корзину!')
    await query.message.delete()


async def show_products(m, products):

    if len(products) == 0:

        await m.answer('Здесь ничего нет 😢')

    else:

        await bot.send_chat_action(m.chat.id, ChatActions.TYPING)

        for idx, title, body, image, price, _ in products:

            markup = product_markup(idx, price)
            text = f'<b>{title}</b>\n\n{body}'

            await m.answer_photo(photo=image,
                                 caption=text,
                                 reply_markup=markup)