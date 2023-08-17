from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

from database.operations.translator_orders import TranslatorOrder
from source.bot_init import dp, bot
from source.config import MAIN_ADMIN
from source.single_chat.admin_commands.start import info_handler_two


# Определение состояний
class TranslatorStates(StatesGroup):
    waiting_count_orders = State()
    displaying_orders = State()


def make_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    
    last_order = types.InlineKeyboardButton('Последний заказ', callback_data='t_last_order')
    count_orders = types.InlineKeyboardButton('Количество заказов', callback_data='t_count_orders')
    choose_count_orders = types.InlineKeyboardButton('Выбрать количество заказов', callback_data='t_choose_orders')
    back_button = types.InlineKeyboardButton("Выход", callback_data='exit_admin')

    keyboard.add(last_order)
    keyboard.add(count_orders)
    keyboard.add(choose_count_orders)
    keyboard.add(back_button)

    return keyboard


@dp.callback_query_handler(lambda callback: callback.data == 'exit_admin', state=TranslatorStates.waiting_count_orders)
async def exit_for_translator(callback: types.CallbackQuery, state: FSMContext):
    # Удаляем сообщение с предыдущей клавиатурой
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await info_handler_two(callback.message)
    await state.finish()


@dp.callback_query_handler(lambda callback: callback.data == 'translator')
async def show_keyboard(callback: types.CallbackQuery):
    await callback.answer()
    await bot.send_message(callback.from_user.id, text='Выберите действие', reply_markup=make_keyboard())
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


@dp.callback_query_handler(lambda query: query.data == 't_last_order')
async def last_order_handler(query: types.CallbackQuery):
    await query.answer()
    # Создаем экземпляр класса TranslatorOrder
    translator_order = TranslatorOrder()
    # Получаем информацию о последнем заказе
    last_order = translator_order.get_latest_order()
    if last_order:
        # Форматируем информацию о последнем заказе
        order_info = f"ID заказа: {last_order[0]}\n" \
                     f"ID пользователя: {last_order[1]}\n" \
                     f"Время заказа: {last_order[2]}\n" \
                     f"Место встречи: {last_order[3]}\n" \
                     f"Номер телефона: {last_order[4]}"
        # Отправляем сообщение с информацией о последнем заказе
        await bot.delete_message(query.message.chat.id, query.message.message_id)
        await bot.send_message(query.from_user.id, order_info)
        await info_handler_two(query.message)
    else:
        # Если нет данных о заказах, отправляем сообщение об этом
        await bot.send_message(query.from_user.id, "Нет данных о заказах")


@dp.callback_query_handler(lambda query: query.data == 't_count_orders')
async def order_count_handler(query: types.CallbackQuery):
    await query.answer()

    # Создаем экземпляр класса TranslatorOrder
    translator_order = TranslatorOrder()
    # Получаем количество заказов
    order_count = translator_order.get_order_count()
    if order_count != 0:
        # Отправляем сообщение с количеством заказов
        await bot.delete_message(query.message.chat.id, query.message.message_id)
        await bot.send_message(query.from_user.id, f"Количество заказов: {order_count}")
        await info_handler_two(query.message)
    else:
        await bot.delete_message(query.message.chat.id, query.message.message_id)
        await bot.send_message(query.from_user.id, 'Таблица с заказми пуста - заказов нет.')
        await info_handler_two(query.message)

@dp.callback_query_handler(lambda query: query.data == 't_choose_orders')
async def choose_count_orders(query: types.CallbackQuery):
    await query.answer()
    await query.message.answer('Введите количество заказов которое хотите просматривать (от 1 до 10)')
    await TranslatorStates.waiting_count_orders.set()


# Обработчик ввода количества заказов
@dp.message_handler(state=TranslatorStates.waiting_count_orders)
async def process_count_orders(message: types.Message, state: FSMContext):
    count_orders = int(message.text)
    async with state.proxy() as data:
        data['count_orders'] = count_orders
        data['offset'] = 0  # Инициализируем смещение (offset) нулевым значением
    await show_orders(message, state)


async def show_orders(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        count_orders = data['count_orders']
        offset = data['offset']
        table = TranslatorOrder()
        orders = table.get_orders(count_orders, offset)

        if len(orders) == 0:
            await message.answer('Нет доступных заказов.')
            await bot.delete_message(message.chat.id, message.message_id)
            await info_handler_two(message)
            return

        orders_info = []
        for order in orders:
            order_info = f"ID заказа: {order[0]}\n" \
                         f"ID пользователя: {order[1]}\n" \
                         f"Время заказа: {order[2]}\n" \
                         f"Место встречи: {order[3]}\n" \
                         f"Номер телефона: {order[4]}"
            orders_info.append(order_info)

        orders_text = "\n\n".join(orders_info)
        markup = types.InlineKeyboardMarkup()
        next_button = types.InlineKeyboardButton('Следующие ➡️', callback_data='t_show_orders_next')
        
        back_button = types.InlineKeyboardButton('Выход', callback_data='exit_admin')
        if offset == 0:
            markup.add(next_button)
            markup.add(back_button)
        else:
            prev_button = types.InlineKeyboardButton('⬅️ Предыдущие', callback_data='t_show_orders_prev')
            markup.row(prev_button, next_button)
            markup.add(back_button)
        await bot.delete_message(message.chat.id, message.message_id)
        await message.answer(orders_text, reply_markup=markup)

# Обработчик для перемещения по таблице (влево или вправо)
@dp.callback_query_handler(lambda query: query.data in ['t_show_orders_prev', 't_show_orders_next'], state=TranslatorStates.waiting_count_orders)
async def navigate_orders(query: types.CallbackQuery, state: FSMContext):
    await query.answer()

    async with state.proxy() as data:
        count_orders = data['count_orders']
        offset = data['offset']

        if query.data == 't_show_orders_prev':
            offset -= count_orders
        elif query.data == 't_show_orders_next':
            offset += count_orders

        data['offset'] = max(0, offset)  # Убеждаемся, что смещение не станет отрицательным

    await show_orders(query.message, state)