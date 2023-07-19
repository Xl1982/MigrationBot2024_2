from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from source.single_chat.admin_commands.start import info_handler
from source.config import MAIN_ADMIN
from source.bot_init import dp, bot
from source.logger_bot import logger
from source.data.classes.add_chat import ChatManager


class SomeState(StatesGroup):
    waiting_for_message = State()


# Обработчик нажатия на кнопку "Отправить сообщение в группы"
# Работает только если нажатие было от главного админа (в принципе можно будет всё это запилить под список или под хранимые данные в json файле)
@dp.callback_query_handler(lambda c: c.data == 'send_messages' and c.from_user.id == MAIN_ADMIN)
async def send_messages_handler(callback_query: types.CallbackQuery):
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Назад"))
    
    await bot.send_message(callback_query.from_user.id, "Введите текст сообщения для рассылки:", reply_markup=markup)
    await SomeState.waiting_for_message.set()

# Обработчик ввода текста администратором
@dp.message_handler(state=SomeState.waiting_for_message)
async def send_message_to_chats(message: types.Message, state: FSMContext):
    file_name = "source\data\chats.json"
    chat_manager = ChatManager(file_name)
    # Получаем текст сообщения от администратора
    text = message.text
    if text == 'Назад':
        await info_handler(message)
        await state.finish()
        return

    # Получаем список чатов (chat_id) с помощью метода get_all_chats()
    chat_ids = chat_manager.get_all_chats()

    # Отправляем сообщение в каждый чат из списка chat_ids
    for chat_id in chat_ids:
        try:
            await bot.send_message(chat_id, text)
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения в чат {chat_id}: {e}")

    # Сбрасываем состояние ожидания
    await state.finish()
    await bot.send_message(message.from_user.id, "Сообщение успешно разослано.", reply_markup=ReplyKeyboardRemove())
    await info_handler(message)