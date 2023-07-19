from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from source.single_chat.admin_commands.start import info_handler
from source.config import CHATS_ID, MAIN_ADMIN
from source.bot_init import dp, bot
from source.logger_bot import logger


class SomeState(StatesGroup):
    waiting_for_message = State()


# Обработчик нажатия на кнопку "Отправить сообщение в группы"
@dp.callback_query_handler(lambda c: c.data == 'send_messages' and c.from_user.id == MAIN_ADMIN)
async def send_messages_handler(callback_query: types.CallbackQuery):
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Назад"))
    
    await bot.send_message(callback_query.from_user.id, "Введите текст сообщения для рассылки:", reply_markup=markup)
    await SomeState.waiting_for_message.set()


# Обработчик ввода текста администратором
@dp.message_handler(state=SomeState.waiting_for_message)
async def send_message_to_chats(message: types.Message, state: FSMContext):
    # Получаем текст сообщения от администратора
    text = message.text
    if text == 'Назад':
        await info_handler(message)
        await state.finish()
        return
    # Отправляем сообщение в каждый чат из списка CHATS_ID
    for chat_id in CHATS_ID:
        try:
            await bot.send_message(chat_id, text)
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения в чат {chat_id}: {e}")
    # Сбрасываем состояние ожидания
    await state.finish()
    await bot.send_message(message.from_user.id, "Сообщение успешно разослано.", reply_markup=ReplyKeyboardRemove())
    await info_handler(message)