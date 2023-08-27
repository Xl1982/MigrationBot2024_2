import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from source.single_chat.admin_commands.start import info_handler, check_admins, info_handler_two
from source.config import MAIN_ADMIN
from source.bot_init import dp, bot
from source.logger_bot import logger
from source.data.classes.add_chat import ChatManager


class SomeState(StatesGroup):
    waiting_for_photos = State()
    waiting_for_send_message = State()
    waiting_for_send_message_without_photo = State()
    waiting_choose = State()

@dp.callback_query_handler(lambda c: c.data =="back_send_message", state='*')
async def back_button_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    await state.finish()
    await info_handler_two(query.message)

# Обработчик нажатия на кнопку "Отправить сообщение в группы"
@dp.callback_query_handler(lambda c: c.data == 'send_messages' and (c.from_user.id == MAIN_ADMIN or c.from_user.id in check_admins()))
async def send_messages_handler(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)

    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Да', callback_data='yes_photo'))
    markup.add(types.InlineKeyboardButton('Нет', callback_data='no_photo'))
    markup.add(types.InlineKeyboardButton('Назад', callback_data='back_send_message'))
    await bot.send_message(callback_query.from_user.id, "Рассылка будет с фото?", reply_markup=markup)
    await SomeState.waiting_choose.set()


@dp.callback_query_handler(lambda c: c.data == 'yes_photo', state=SomeState.waiting_choose)
async def get_photo(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Назад', callback_data='back_send_message'))
    await query.message.answer('Отправьте фото к сообщению (до 10)', reply_markup=markup)
    await SomeState.waiting_for_photos.set()


# Обработчик для приема фотографий и добавления их в состояние
@dp.message_handler(content_types=types.ContentType.PHOTO, state=SomeState.waiting_for_photos)
async def process_photos(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # Получаем список фотографий из состояния или создаем новый
        photos = data.get('photos', [])

        # Добавляем фотографию в список
        photos.append(message.photo[-1].file_id)
        # Обновляем данные в состоянии
        await state.update_data(photos=photos)
        num_photos_added = len(photos)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Назад', callback_data='back_send_message'))
        if num_photos_added < 10:
            remaining_photos = 10 - num_photos_added
            await message.answer(f"Вы добавили {num_photos_added} фото. Вы можете добавить еще {remaining_photos} фото или отправить текст.",
                                  reply_markup=markup)
        else:
            await message.answer("Вы добавили максимальное количество фото (10). Теперь отправьте текст.", reply_markup=markup)
    await SomeState.waiting_for_send_message.set()


@dp.message_handler(state=SomeState.waiting_for_send_message)
async def send_message_to_chats_with_photo(message: types.Message, state: FSMContext):
    file_name = os.path.join("source", "data", "chats.json")
    chat_manager = ChatManager(file_name)
    async with state.proxy() as data:
        # Получаем информацию о текстовом сообщении и фотографиях из состояния
        text_message = message.text
        photos = data.get('photos', [])

        # Создаем список медиа-элементов для отправки
        media_group = []
        for i, photo in enumerate(photos):
            # Первая фотография будет иметь подпись, остальные - нет
            caption = text_message if i == 0 else None
            media_group.append(types.InputMediaPhoto(media=photo, caption=caption))

        # Получаем список чатов (chat_id) с помощью метода get_all_chat_ids()
        chat_ids = chat_manager.get_all_chat_ids()

        for chat_id in chat_ids:
            chat_info = chat_manager.get_chat_data(chat_id)
            if chat_info['sending_messages']:
                # Отправляем группу фотографий как альбом в каждый чат
                await bot.send_media_group(chat_id, media=media_group)
                await message.answer(f'В чат {chat_info["title"]} сообщение отправлено', reply_markup=ReplyKeyboardRemove())
            else:
                await message.answer(f'В чат {chat_info["title"]} отключена отправка сообщений. Включите в настройках чата через /chats.')

        await state.finish()
        await info_handler_two(message)


@dp.callback_query_handler(lambda c: c.data == 'no_photo', state=SomeState.waiting_choose)
async def get_text_without_photo(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.delete_message(query.message.chat.id, query.message.message_id)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Назад', callback_data='back_send_message'))

    await query.message.answer('Отправьте текст для рассылки в чаты: ', reply_markup=markup)
    await SomeState.waiting_for_send_message_without_photo.set()


@dp.message_handler(state=SomeState.waiting_for_send_message_without_photo)
async def send_message_to_chats(message: types.Message, state: FSMContext):
    file_name = os.path.join("source", "data", "chats.json")
    chat_manager = ChatManager(file_name)
    # Получаем текст сообщения от администратора
    text = message.text

    # Получаем список чатов (chat_id) с помощью метода get_all_chat_ids()
    chat_ids = chat_manager.get_all_chat_ids()

    # Отправляем сообщение в каждый чат из списка chat_ids
    for chat_id in chat_ids:
        try:
            chat_info = chat_manager.get_chat_data(chat_id)
            if chat_info['sending_messages']:
                await bot.send_message(chat_id, text)
                await message.answer(f'В чат {chat_info["title"]} сообщение отправлено', reply_markup=ReplyKeyboardRemove())
            else:
                await message.answer(f'В чат {chat_info["title"]} отключена отправка сообщений. Включите в настройках чата через /chats.')
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения в чат {chat_id}: {e}")

    # Сбрасываем состояние ожидания
    await state.finish()
    await info_handler_two(message)