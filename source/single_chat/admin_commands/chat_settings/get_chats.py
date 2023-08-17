import os

from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup

from source.data.classes.add_chat import ChatManager
from source.bot_init import dp


class ChatStates(StatesGroup):
    ...


@dp.callback_query_handler(lambda c: c.data == 'chats')
async def show_chats(query: types.CallbackQuery):
    path = os.path.join('source', 'data', 'chats.json')
    chat_manager = ChatManager(path)

    chat_info = chat_manager.get_all_chats()
    keyboard = types.InlineKeyboardMarkup()
    for chat_id, chat_name in chat_info.items():
        keyboard.add(types.InlineKeyboardButton(chat_name, callback_data=chat_id))
    
    await query.message.answer('Выберите чат для настройки: ', reply_markup=keyboard)

