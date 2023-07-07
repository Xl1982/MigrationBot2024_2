'''Получение информации о заказах такси'''
import math

from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext


from database.operations.taxi_orders import TaxiOrder

from source.bot_init import dp, bot
from source.single_chat.admin_commands.start import info_handler


def make_back_button():
    # Создаем объект инлайн клавиатуры
    keyboard = types.InlineKeyboardMarkup() 
    keyboard.add(types.InlineKeyboardButton('Выход', callback_data='exit'))
    # Возвращаем клавиатуру
    return keyboard

# Создаем функцию для генерации инлайн клавиатуры с кнопками для выбора действия с заказами такси
def make_taxi_keyboard():
    # Создаем объект инлайн клавиатуры
    keyboard = types.InlineKeyboardMarkup()
    # Добавляем кнопки с текстом и коллбэк-данными
    keyboard.add(types.InlineKeyboardButton("Последний заказ", callback_data="last_order"))
    keyboard.add(types.InlineKeyboardButton("Количество заказов", callback_data="order_count"))
    keyboard.add(types.InlineKeyboardButton("Выбрать количество заказов", callback_data="choose_orders"))
    keyboard.add(types.InlineKeyboardButton('Выход', callback_data='exit'))
    # Возвращаем клавиатуру
    return keyboard


# Создаем функцию для формирования инлайн клавиатуры с кнопками листания
def make_pagination_keyboard(limit, offset, total_orders):
    # Создаем объект инлайн клавиатуры
    keyboard = types.InlineKeyboardMarkup()
    
    # Создаем список кнопок
    buttons = []
    
    # Если offset больше нуля, то добавляем кнопку "Назад" с callback_data в виде limit:offset-limit
    if offset > 0:
        buttons.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"{limit}:{offset-limit}"))
    
    # Если offset плюс limit меньше общего количества заказов, то добавляем кнопку "Вперед" с callback_data в виде limit:offset+limit
    if offset + limit < total_orders:
        buttons.append(types.InlineKeyboardButton("Вперед ➡️", callback_data=f"{limit}:{offset+limit}"))
    
    # Добавляем кнопки в клавиатуру
    keyboard.add(*buttons)
    keyboard.add(types.InlineKeyboardButton('Выход', callback_data='exit'))

    # Возвращаем клавиатуру
    return keyboard


# Определяем класс StatesGroup с разными состояниями
class OrderStates(StatesGroup):
    waiting_for_count = State()

@dp.callback_query_handler(lambda c: c.data == 'exit', state=OrderStates.waiting_for_count)
async def exit_from_taxi_info(callback: types.CallbackQuery, state: FSMContext):
    # Удаляем сообщение с предыдущей клавиатурой
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await info_handler(callback.message)
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'exit')
async def exit_from_taxi_info(callback: types.CallbackQuery):
    # Удаляем сообщение с предыдущей клавиатурой
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await info_handler(callback.message)
    
        

# Регистрируем обработчик для коллбэк-запроса с данными 'taxi'
@dp.callback_query_handler(lambda c: c.data == 'taxi')
async def give_choose_taxi(callback: types.CallbackQuery):
    # Отправляем сообщение с текстом и инлайн клавиатурой
    await bot.send_message(callback.from_user.id, "Выберите действие с заказами такси:", reply_markup=make_taxi_keyboard())
    # Удаляем сообщение с предыдущей клавиатурой
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

# Регистрируем обработчик для коллбэк-запроса с данными 'last_order'
@dp.callback_query_handler(lambda c: c.data == 'last_order')
async def show_last_order(callback: types.CallbackQuery):
    taxi_order = TaxiOrder()
    last_order = taxi_order.get_last_order()
    
    keyboard = make_back_button()

    if last_order:
        # Формируем текст сообщения с markdown-форматированием
        text = f"🚕 Последний заказ:\n\n" \
            f"**Номер заказа:** {last_order['order_id']}\n" \
            f"**ID пользователя:** {last_order['user_id']}\n" \
            f"**Время заказа:** {last_order['order_time']}\n" \
            f"**Откуда:** {last_order['order_from']}\n" \
            f"**Куда:** {last_order['order_to']}\n" \
            f"**Телефон:** {last_order['phone_number']}"
    else:
        text = f'Увы, но заказов в базе данных нет...'
        
    # Отправляем сообщение с текстом и указываем параметр parse_mode='Markdown'
    await bot.send_message(callback.from_user.id, text, parse_mode='Markdown', reply_markup=keyboard)
    # Удаляем сообщение с предыдущей клавиатурой
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

# Регистрируем обработчик для коллбэк-запроса с данными 'order_count'
@dp.callback_query_handler(lambda c: c.data == 'order_count')
async def show_order_count(callback: types.CallbackQuery):
    taxi_order = TaxiOrder()
    count_orders = taxi_order.get_order_count()

    keyboard = make_back_button()

    # Пока что просто отправляем сообщение с текстом
    await bot.send_message(callback.from_user.id, f"Количество заказов записанных в базе данных: {count_orders}", reply_markup=keyboard)
    # Удаляем сообщение с предыдущей клавиатурой
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

# Регистрируем обработчик для коллбэк-запроса с данными 'choose_orders'
@dp.callback_query_handler(lambda c: c.data == 'choose_orders')
async def choose_orders(callback: types.CallbackQuery):
    
    # Переходим в состояние ожидания ввода количества заказов
    await OrderStates.waiting_for_count.set()
    
    keyboard = make_back_button()

    # Отправляем сообщение с текстом
    await bot.send_message(callback.from_user.id, "Напишите количество заказов которое хотите выводить (от 1 до 10): ", reply_markup=keyboard)
    # Удаляем сообщение с предыдущей клавиатурой
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

# Регистрируем обработчик для текстовых сообщений в состоянии ожидания ввода количества заказов
@dp.message_handler(state=OrderStates.waiting_for_count)
async def show_orders(message: types.Message, state: FSMContext):
    
    # Проверяем, что пользователь ввел корректное число заказов
    try:
        limit = int(message.text)
        if limit < 1 or limit > 10:
            raise ValueError
    except ValueError:
        # Если нет, то отправляем сообщение с ошибкой и возвращаемся в то же состояние
        await message.reply("Пожалуйста, введите число от 1 до 10")
        return
    
    # Если да, то получаем общее количество заказов в таблице
    taxi_order = TaxiOrder()
    total_orders = taxi_order.get_order_count() # Это метод, который возвращает число заказов в таблице
    
    # Устанавливаем смещение равным нулю
    offset = 0
    
    # Получаем список заказов из базы данных с заданным лимитом и смещением
    orders = taxi_order.get_orders(limit, offset)
    
    # Формируем текст сообщения с информацией о заказах
    if orders:
        text = f"🚕 Вот последние {limit} заказов:\n\n"
        for order in orders:
            text += f"**Номер заказа:** {order['order_id']}\n" \
                    f"**ID пользователя:** {order['user_id']}\n" \
                    f"**Время заказа:** {order['order_time']}\n" \
                    f"**Откуда:** {order['order_from']}\n" \
                    f"**Куда:** {order['order_to']}\n" \
                    f"**Телефон:** {order['phone_number']}\n\n"
        
        # Вычисляем номер текущей страницы и общее количество страниц
        page = offset // limit + 1
        total_pages = math.ceil(total_orders / limit)
        
        # Добавляем подпись с номером страницы
        text += f"Страница {page} из {total_pages}"
        
    else:
        text = 'Заказов в базе данных пока нет...'
    
    # Создаем инлайн клавиатуру с кнопками листания
    keyboard = make_pagination_keyboard(limit, offset, total_orders)
    
    # Отправляем сообщение с текстом и клавиатурой и указываем параметр parse_mode='Markdown'
    await message.answer(text, reply_markup=keyboard, parse_mode='Markdown')
    
# Регистрируем обработчик для callback_query от инлайн кнопок
@dp.callback_query_handler(state=OrderStates.waiting_for_count)
async def pagination_callback(call: types.CallbackQuery):
    
    # Получаем данные из callback_data в виде limit:offset
    data = call.data.split(":")
    
    # Преобразуем данные в целые числа
    limit = int(data[0])
    offset = int(data[1])
    
    # Получаем общее количество заказов в таблице
    taxi_order = TaxiOrder()
    total_orders = taxi_order.get_order_count() # Это метод, который возвращает число заказов в таблице
    
    # Получаем список заказов из базы данных с заданным лимитом и смещением
    orders = taxi_order.get_orders(limit, offset)
    
    # Формируем новый текст сообщения с информацией о заказах
    if orders:
        text = f"🚕 Вот последние {limit} заказов:\n\n"
        for order in orders:
            text += f"**Номер заказа:** {order['order_id']}\n" \
                    f"**ID пользователя:** {order['user_id']}\n" \
                    f"**Время заказа:** {order['order_time']}\n" \
                    f"**Откуда:** {order['order_from']}\n" \
                    f"**Куда:** {order['order_to']}\n" \
                    f"**Телефон:** {order['phone_number']}\n\n"
        
        # Вычисляем номер текущей страницы и общее количество страниц
        page = offset // limit + 1
        total_pages = math.ceil(total_orders / limit)
        
        # Добавляем подпись с номером страницы
        text += f"Страница {page} из {total_pages}"
        
    else:
        text = 'Заказов в базе данных пока нет...'
    
    # Создаем инлайн клавиатуру с кнопками листания
    keyboard = make_pagination_keyboard(limit, offset, total_orders)
    
    # Подтверждаем получение callback_query
    await call.answer()
    
    # Редактируем исходное сообщение с новым текстом и клавиатурой
    await call.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')