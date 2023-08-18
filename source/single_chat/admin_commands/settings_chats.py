import os

from aiogram import types, utils
from aiogram.dispatcher import FSMContext

from source.single_chat.admin_commands.start import ChatEditStates, start_chats_settings
from source.bot_init import dp, bot
from source.data.classes.add_chat import ChatManager

PATH = os.path.join('source', 'data', 'chats.json')
    

@dp.callback_query_handler(lambda query: query.data == 'back_chat_edit', state='*')
async def back_callback(query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    await query.answer()
    await state.finish()
    await start_chats_settings(query.message)


def make_keyboard_settings(chat_id):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton('Рассылка сообщений', callback_data=f"toggle_sending_messages_{chat_id}"),
        types.InlineKeyboardButton('Прогноз погоды', callback_data=f"toggle_send_weather_{chat_id}"),
        types.InlineKeyboardButton('Курс валюты', callback_data=f"toggle_send_currency_{chat_id}"),
        types.InlineKeyboardButton('Покупка валюты', callback_data=f"toggle_send_purchase_currency_{chat_id}"),
        types.InlineKeyboardButton('Приветсвенное сообщение', callback_data=f'edit_welcome_message_{chat_id}'),
        types.InlineKeyboardButton('Текстовые сообщения', callback_data=f'edit_text_messages_{chat_id}'),
        types.InlineKeyboardButton('ID чата', callback_data=f'chat_id_{chat_id}'),
        types.InlineKeyboardButton('Настройки погоды', callback_data=f'weather_settings_{chat_id}')
    )
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data='back_chat_edit'))

    return keyboard


@dp.callback_query_handler(lambda query: query.data.startswith('chat_id_'), state=ChatEditStates.choose_chat)
async def get_chat_id(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    chat_id = query.data.split('_')[-1]
    await query.message.answer(f'Chat ID текущего чата: <code>{chat_id}</code>')
    await state.finish()
    await start_chats_settings(query.message)


# Начало ветки действий. Выводим пользователю кнопки для настройки
@dp.callback_query_handler(lambda query: query.data.startswith('back_edit_welcome'), state=ChatEditStates.get_welcome_text)
@dp.callback_query_handler(lambda query: query.data in ChatManager.get_all_chat_ids_static(os.path.join('source', 'data', 'chats.json')),
                            state=ChatEditStates.choose_chat)
async def show_chat_setting(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.delete_message(query.message.chat.id, query.message.message_id)


    data = query.data
    if data.startswith('back_edit_welcome'):
        chat_id = data.split('_')[-1]
        await ChatEditStates.choose_chat.set()
    else:
        chat_id = data
    chat_manager = ChatManager(PATH)
    chat_data = chat_manager.get_chat_data(chat_id)

    # Формируем текст с текущими параметрами чата
    settings_text = f"Текущие параметры чата '{chat_data.get('title', 'Нет названия')}':\n"
    settings_text += f"Рассылка сообщений: {'Включена' if chat_data.get('sending_messages') else 'Выключена'}\n"
    settings_text += f"Прогноз погоды: {'Включен' if chat_data.get('send_weather') else 'Выключен'}\n"
    settings_text += f"Курс валюты: {'Включен' if chat_data.get('send_currency') else 'Выключен'}\n"
    settings_text += f"Покупка валюты: {'Включена' if chat_data.get('send_purchase_currency') else 'Выключена'}"

    # Выводим текущие параметры чата
    settings_message = await bot.send_message(query.message.chat.id, settings_text, reply_markup=make_keyboard_settings(chat_id))
    await state.update_data(settings_message_id=settings_message.message_id)
    await state.update_data(chat_id=str(chat_id))

# Переключатель в настройках (выключает-включает одну из четырёх настроек)
@dp.callback_query_handler(lambda query: query.data.startswith("toggle_"), state=ChatEditStates.choose_chat)
async def toggle_chat_setting(query: types.CallbackQuery, state: FSMContext):
    await query.answer()

    chat_id = query.data.split('_')[-1]
    setting_type = query.data.split('_')[1] + "_" + query.data.split('_')[2]

    chat_manager = ChatManager(PATH)
    chat_data = chat_manager.get_chat_data(chat_id)

    state_data = await state.get_data()

    # Определяем какое поле в JSON файле нужно изменить и меняем его значение
    if setting_type == 'sending_messages':
        chat_manager.update_chat_data(chat_id, 'sending_messages', not chat_data.get('sending_messages', False))
    elif setting_type == 'send_weather':
        chat_manager.update_chat_data(chat_id, 'send_weather', not chat_data.get('send_weather', False))
    elif setting_type == 'send_currency':
        chat_manager.update_chat_data(chat_id, 'send_currency', not chat_data.get('send_currency', False))
    elif setting_type == 'send_purchase':
        chat_manager.update_chat_data(chat_id, 'send_purchase_currency', not chat_data.get('send_purchase_currency', False))

    chat_data = chat_manager.get_chat_data(chat_id)

    # Формируем текст с текущими параметрами чата
    settings_text = f"Текущие параметры чата '{chat_data.get('title', 'Нет названия')}':\n"
    settings_text += f"Рассылка сообщений: {'Включена' if chat_data.get('sending_messages') else 'Выключена'}\n"
    settings_text += f"Прогноз погоды: {'Включен' if chat_data.get('send_weather') else 'Выключен'}\n"
    settings_text += f"Курс валюты: {'Включен' if chat_data.get('send_currency') else 'Выключен'}\n"
    settings_text += f"Покупка валюты: {'Включена' if chat_data.get('send_purchase_currency') else 'Выключена'}"

    # Удалить старое сообщение, если есть
    async with state.proxy() as data:
        settings_message_id = data.get('settings_message_id')
        if settings_message_id:
            try:
                await bot.delete_message(chat_id=query.message.chat.id, message_id=settings_message_id)
            except utils.exceptions.MessageCantBeDeleted:
                pass

    # Отправить новое сообщение с параметрами чата и сохранить его message_id в state
    new_message = await bot.send_message(query.message.chat.id, settings_text, reply_markup=make_keyboard_settings(state_data['chat_id']))
    async with state.proxy() as data:
        data['settings_message_id'] = new_message.message_id

    await query.answer("Настройка изменена")

# Ветка для изменения welcome_message
# Обработчик для редактирования приветственного сообщения
@dp.callback_query_handler(lambda query: query.data.startswith('edit_welcome_message_'),
                            state=ChatEditStates.choose_chat)
async def edit_welcome_message(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    
    # Получем данные чата
    chat_manager = ChatManager(PATH)
    chat_id = query.data.split('_')[-1]
    await state.update_data(chat_id=chat_id)
    chat_data = chat_manager.get_chat_data(chat_id)
    # Формируем текст и клавиатуру
    keyboard = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data=f"back_edit_welcome_{chat_id}"))
    text = (f'Ваше текущее приветственное сообщение:\n\n{chat_data["welcome_message"]} \n\nЧтобы изменить его, введите новое сообщение.'
            ' Для выхода нажмите на кнопку.')
    # Отправляем сообщение
    await query.message.answer(text, reply_markup=keyboard)
    await ChatEditStates.get_welcome_text.set()

@dp.message_handler(state=ChatEditStates.get_welcome_text)
async def save_new_welcome_message(message: types.Message, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id - 1)
    # Получем данные чата
    state_data = await state.get_data()
    chat_manager = ChatManager(PATH)
    chat_data = chat_manager.get_chat_data(state_data['chat_id'])
    # Сохраняем в состояние старое сообщение, обновляем данные с новым
    await state.update_data(old_message=chat_data['welcome_message'])
    chat_manager.update_chat_data(state_data['chat_id'], 'welcome_message', message.text)
    chat_data = chat_manager.get_chat_data(state_data['chat_id'])
    # Формируем клавиатуру
    keyboard = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Подтвердить', callback_data=f'apply_edit_welcome'))
    keyboard.add(types.InlineKeyboardButton('Отменить', callback_data=f'cancel_edit_welcome_{state_data["chat_id"]}'))
    # Отправляем текст и клавиатуру
    text = (f'Ваше новое приветственное сообщение:\n\n {chat_data["welcome_message"]}')
    await message.answer(text, reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data == 'apply_edit_welcome', state=ChatEditStates.get_welcome_text)
async def apply_new_welcome_message(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    # Просто переходим к началу редактирования настроек у чата
    await query.answer('Сообщение сохранено')
    await ChatEditStates.choose_chat.set()
    await start_chats_settings(query.message)


@dp.callback_query_handler(lambda query: query.data == 'cancel_edit_welcome', state=ChatEditStates.get_welcome_text)
async def cancel_new_welcome_message(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    # Получаем данные чата и обновляем их
    state_data = await state.get_data()
    chat_manager = ChatManager(PATH)
    chat_manager.update_chat_data(state_data['chat_id'], 'welcome_message', state_data['old_message'])
    # Отправляем сообщение и переходим к настройкам чата
    await query.message.answer(f'Старое сообщение оставлено:\n\n {state_data["old_message"]}')
    await ChatEditStates.choose_chat.set()
    await start_chats_settings(query.message)

    
# Ветка изменения настроек погоды

@dp.callback_query_handler(lambda c: c.data.startswith('weather_settings_'), state=ChatEditStates.choose_chat)
async def start_weather_setting(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    
    
    chat_manager = ChatManager(PATH)
    chat_id = query.data.split('_')[-1]
    chat_info = chat_manager.get_chat_data(chat_id)
    city_ru = chat_info['weather_settings']['city_ru']
    city_en = chat_info['weather_settings']['city_en']
    await state.update_data(chat_id=chat_id)

    text = f'{city_ru} | {city_en}'

    keyboard = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выход', callback_data='back_chat_edit'))

    await query.message.answer(f'Введите название города на русском языке. Текущий город - {text}.', reply_markup=keyboard)
    await ChatEditStates.wait_ru_city.set()

@dp.message_handler(state=ChatEditStates.wait_ru_city)
async def get_ru_city(message: types.Message, state: FSMContext):
    await state.update_data(city_ru=message.text)

    keyboard = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выход', callback_data='back_chat_edit'))
    await message.answer('Название города на русском сохранено. Теперь введите название города на английском. Необходимо для нахождения прогноза погоды.')
    await ChatEditStates.wait_en_city.set()

@dp.message_handler(state=ChatEditStates)
async def get_en_city(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    city_ru = state_data['city_ru']
    city_en = message.text
    chat_id = state_data['chat_id']

    chat_manager = ChatManager(PATH)

    weather_settings = {
        'city_ru': city_ru,
        'city_en': city_en
    }
    text = f'{city_ru} | {city_en}'

    chat_manager.update_chat_data(chat_id, 'weather_settings', weather_settings)
    await message.answer(f'Название успешно сохранено. Текущее название города - {text}.')
    await state.finish()
    await start_chats_settings(message)
