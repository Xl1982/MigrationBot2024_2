import re
import os

from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

from source.data.classes.messages import TextMessagesStorage
from source.bot_init import dp, bot
from source.single_chat.admin_commands.start import info_handler_two

weekdays = {
    "Monday": "Понедельник",
    "Tuesday": "Вторник",
    "Wednesday": "Среда",
    "Thursday": "Четверг",
    "Friday": "Пятница",
    "Saturday": "Суббота",
    "Sunday": "Воскресенье",
}


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
    wait_choose = State()
    wait_photos = State()


def retranslate_day(day_en):
    '''return: day_ru'''
    return weekdays[day_en]

# Функция для генерации клавиатуры с днями недели
def generate_weekdays_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    for day_en, day_ru in weekdays.items():
        callback_data = f"messages_day_{day_en.lower()}"
        keyboard.add(types.InlineKeyboardButton(day_ru, callback_data=callback_data))
    keyboard.add(types.InlineKeyboardButton('Выход', callback_data='messages_exit'))
    return keyboard


@dp.callback_query_handler(lambda c: c.data == 'messages_exit', state='*')
async def exit_from_states(query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    await info_handler_two(query.message)
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
        await info_handler_two(query.message)
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
        await query.message.answer(f"Сообщений на {retranslate_day(chosen_day)} нет.")
        await state.finish()
        return

    # Отправляем список сообщений и предлагаем выбрать сообщение для удаления
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for time_sent in messages:
        keyboard.add(types.InlineKeyboardButton(time_sent, callback_data=f"delete_message_{time_sent}"))
    keyboard.add(types.InlineKeyboardButton('Выход', callback_data='messages_exit'))

    await query.message.answer(f"Выберите время отправки сообщения на {retranslate_day(chosen_day)}, которое нужно удалить:", reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data.startswith('messages_day_'), state=MessagesState.current_messages)
async def choose_day_to_current_message(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    
    # Получаем выбранный день недели
    chosen_day = query.data.split('_')[2].capitalize()
    
    # Получаем список сообщений на указанный день
    messages = storage.get_messages_for_day(chosen_day)
    
    if not messages:
        await query.message.answer(f"Сообщений на {retranslate_day(chosen_day)} нет.")
        await state.finish()
        return

    # Отправляем каждое сообщение отдельно
    for message in messages:
        time_sent = message['time_sent']
        text = message['text']
        photos = message['photos']
        # chat_id = message['chat_id']
        text = f'<b>Время отправки: {time_sent}</b>\nТекст:\n' + text
        if photos:
            media_group = []
            for i, photo in enumerate(photos):
                # Первая фотография будет иметь подпись, остальные - нет
                caption = text if i == 0 else None
                media_group.append(types.InputMediaPhoto(media=photo, caption=caption))                    
                await query.message.answer_media_group(media_group) 
        else:
            # Отправляем время отправки и текст
            await query.message.answer(f"<b>Время отправки: {time_sent}</b>\nТекст:\n {text}")

    # Завершаем состояние
    await state.finish()

# Обработчик для получения времени при добавлении сообщения
@dp.message_handler(state=MessagesState.add_time)
async def add_message_time(message: types.Message, state: FSMContext):
    # Проверяем, соответствует ли формат времени ЧЧ:ММ
    keyboard = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('Да', callback_data='photo_mess_yes'), 
                                                types.InlineKeyboardButton('Нет', callback_data='photo_mess_no'))
    keyboard.add(types.InlineKeyboardButton('Выход', callback_data='messages_exit'))

    time_sent = message.text.strip()
    if not re.match(r'^\d{1,2}:\d{2}$', time_sent):
        await message.reply("Неправильный формат времени. Введите время в формате ЧЧ:ММ (например, 12:30):", reply_markup=keyboard)
        return

    # Сохраняем время отправки в состояние
    await state.update_data(time_sent=time_sent)

    # Просим ввести текст сообщения
    await MessagesState.wait_choose.set()
    await message.answer("Сообщение будет с фото?", reply_markup=keyboard)

# Ответление для сохранения фото

# Если фотографии будут, тогда просим их отправить
@dp.callback_query_handler(lambda c: c.data == 'photo_mess_yes', state=MessagesState.wait_choose)
async def message_with_photo(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Выход', callback_data='messages_exit'))
    await query.message.answer('Отправьте фото к сообщению (до 10)', reply_markup=markup)
    await MessagesState.wait_photos.set()


# Обработчик для приема фотографий и добавления их в состояние
@dp.message_handler(content_types=types.ContentType.PHOTO, state=MessagesState.wait_photos)
async def save_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # Получаем список фотографий из состояния или создаем новый
        photos = data.get('photos', [])

        # Добавляем фотографию в список
        photos.append(message.photo[-1].file_id)
        # Обновляем данные в состоянии
        await state.update_data(photos=photos)
        num_photos_added = len(photos)
        if num_photos_added < 10:
            remaining_photos = 10 - num_photos_added
            await message.answer(f"Вы добавили {num_photos_added} фото. Вы можете добавить еще {remaining_photos} фото или отправить текст.")
        else:
            await message.answer("Вы добавили максимальное количество фото (10). Теперь отправьте текст.")
    await MessagesState.add_text.set()

# Если без фото
@dp.callback_query_handler(lambda c: c.data == 'photo_mess_no', state=MessagesState.wait_choose)
async def message_without_photo(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Выход', callback_data='messages_exit'))
    await query.message.answer('Отправьте текст сообщения', reply_markup=markup)
    await MessagesState.add_text.set()

# Обработчик для получения текста сообщения при добавлении
@dp.message_handler(state=MessagesState.add_text)
async def add_message_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])
    chosen_day = data.get('chosen_day')
    time_sent = data.get('time_sent')
    text_message = message.text

    if photos:
        storage.add_message(chosen_day, time_sent, text_message, message.chat.id, photos)
    else:
        storage.add_message(chosen_day, time_sent, text_message, message.chat.id)
    await message.reply(f"Сообщение успешно добавлено на {retranslate_day(chosen_day)} в {time_sent}.")
    await info_handler_two(message)
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
    await query.message.answer(f"Сообщение на {retranslate_day(chosen_day)} в {time_sent} успешно удалено.")

    # Завершаем состояние
    await state.finish()