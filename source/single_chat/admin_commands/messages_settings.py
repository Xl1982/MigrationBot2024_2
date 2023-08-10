import re
import os

from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

from source.data.classes.messages import TextMessagesStorage
from source.bot_init import dp, bot
from source.single_chat.admin_commands.start import info_handler

# Определите путь к файлу, используя модуль os
path = os.path.join('source', 'data', 'messages.json')

# Создайте или работайте с файлом по указанному пути
storage = TextMessagesStorage(path)

# Состояния
class MessagesState(StatesGroup):
    current_messages = State()
    add_messages = State()
    add_time = State()
    add_text = State()
    delete_messages = State()


# Функция для генерации клавиатуры с днями недели
def generate_weekdays_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for day in weekdays:
        callback_data = f"messages_day_{day.lower()}"
        keyboard.add(types.InlineKeyboardButton(day, callback_data=callback_data))
    keyboard.add(types.InlineKeyboardButton('Выход', callback_data='messages_exit'))
    return keyboard


@dp.callback_query_handler(lambda c: c.data == 'messages_exit', state='*')
async def exit_from_states(query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    await info_handler(query.message)
    await state.finish()


# 
# Точка входа текущей ветки
# 
@dp.callback_query_handler(lambda c: c.data == 'messages')
async def start_settings(query: types.CallbackQuery):
    await query.answer()
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Текущие сообщения', callback_data='messages_current'))
    keyboard.add(types.InlineKeyboardButton('Добавить сообщение', callback_data='messages_add'))
    keyboard.add(types.InlineKeyboardButton('Удалить сообщение', callback_data='messages_delete'))
    keyboard.add(types.InlineKeyboardButton('Выход', callback_data='messages_exit'))
    
    await query.message.answer('Выберите действие:', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data.startswith('messages_'))
async def current_messages(query: types.CallbackQuery):
    await query.answer()
    choose = query.data.split('_')[1]
    if choose == 'current':
        await MessagesState.current_messages.set()
    elif choose == 'add':
        await MessagesState.add_messages.set()
    elif choose == 'delete':
        await MessagesState.delete_messages.set()
    elif choose == 'exit':
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        await info_handler(query.message)
        return
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    await query.message.answer('Выберите день недели:', reply_markup=generate_weekdays_keyboard())


# Обработчик для выбора дня недели при добавлении сообщений
@dp.callback_query_handler(lambda c: c.data.startswith('messages_day_'), state=MessagesState.add_messages)
async def choose_day_to_add_message(query: types.CallbackQuery, state: FSMContext):
    await query.answer()

    # Получаем выбранный день недели
    chosen_day = query.data.split('_')[2].capitalize()
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    await state.update_data(chosen_day=chosen_day)
    await MessagesState.add_time.set()
    await query.message.answer('Введите время отправки сообщения в формате ЧЧ:ММ (например, 12:30):')


# Обработчик для выбора дня недели при удалении сообщений
@dp.callback_query_handler(lambda c: c.data.startswith('messages_day_'), state=MessagesState.delete_messages)
async def choose_day_to_delete_message(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    # Получаем выбранный день недели
    chosen_day = query.data.split('_')[2].capitalize()
    # Получаем список сообщений на указанный день
    messages = storage.get_messages_for_day(chosen_day)
    if not messages:
        await query.message.answer(f"Сообщений на {chosen_day} нет.")
        await state.finish()
        return

    # Отправляем список сообщений и предлагаем выбрать сообщение для удаления
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for time_sent in messages:
        keyboard.add(types.InlineKeyboardButton(time_sent, callback_data=f"delete_message_{time_sent}"))
    keyboard.add(types.InlineKeyboardButton('Выход', callback_data='messages_exit'))

    await query.message.answer(f"Выберите время отправки сообщения на {chosen_day}, которое нужно удалить:", reply_markup=keyboard)


# Обработчик для выбора дня недели при просмотре сообщений
@dp.callback_query_handler(lambda c: c.data.startswith('messages_day_'), state=MessagesState.current_messages)
async def choose_day_to_current_message(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    # Получаем выбранный день недели
    chosen_day = query.data.split('_')[2].capitalize()
    # Получаем список сообщений на указанный день
    messages = storage.get_messages_for_day(chosen_day)
    if not messages:
        await query.message.answer(f"Сообщений на {chosen_day} нет.")
        await state.finish()
        return

    # Формируем ответ с сообщениями на выбранный день
    response = f"Сообщения на {chosen_day}:"
    for time_sent, message in messages.items():
        response = f"\n\nВремя отправки: {time_sent}\n{message}"
        await query.message.answer(response)

    # Завершаем состояние
    await state.finish()

# Обработчик для получения времени при добавлении сообщения
@dp.message_handler(state=MessagesState.add_time)
async def add_message_time(message: types.Message, state: FSMContext):
    # Проверяем, соответствует ли формат времени ЧЧ:ММ
    keyboard = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выход', callback_data='messages_exit'))
    time_sent = message.text.strip()
    if not re.match(r'^\d{1,2}:\d{2}$', time_sent):
        await message.reply("Неправильный формат времени. Введите время в формате ЧЧ:ММ (например, 12:30):", reply_markup=keyboard)
        return

    # Сохраняем время отправки в состояние
    await state.update_data(time_sent=time_sent)

    # Просим ввести текст сообщения
    await MessagesState.add_text.set()
    await message.reply("Введите текст сообщения:", reply_markup=keyboard)

# Обработчик для получения текста сообщения при добавлении
@dp.message_handler(state=MessagesState.add_text)
async def add_message_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    chosen_day = data.get('chosen_day')
    time_sent = data.get('time_sent')
    text_message = message.text

    # Добавляем сообщение в хранилище
    storage.add_message(chosen_day, time_sent, text_message)
    await message.reply(f"Сообщение успешно добавлено на {chosen_day} в {time_sent}.")
    await info_handler(message)
    # Завершаем состояние
    await state.finish()

# ...

# Обработчик для удаления сообщения по времени отправки
@dp.callback_query_handler(lambda c: c.data.startswith('delete_message_'), state=MessagesState.delete_messages)
async def delete_message(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    # Получаем время отправки выбранного сообщения
    time_sent = query.data.split('_')[2]

    # Получаем выбранный день недели из состояния
    data = await state.get_data()
    chosen_day = data.get('chosen_day')

    # Удаляем сообщение
    storage.delete_message(chosen_day, time_sent)

    # Отправляем сообщение об успешном удалении
    await query.message.answer(f"Сообщение на {chosen_day} в {time_sent} успешно удалено.")

    # Завершаем состояние
    await state.finish()