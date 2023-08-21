import asyncio
import os

from aiogram import types

from source.data.classes.add_chat import ChatManager
from source.bot_init import bot, dp


# Обработчик события присоединения нового участника к группе
@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def welcome_new_member(message: types.Message):
    # Получаем информацию о первом новом участнике
    new_member = message.new_chat_members[0]
    chat_manager = ChatManager(os.path.join('source', 'data', 'chats.json'))
    chat_data = chat_manager.get_chat_data(str(message.chat.id))
    
    # Приветственное сообщение для нового участника
    welcome_text = chat_data['welcome_message']

    # Отправляем приветственное сообщение новому участнику
    welcome_message = await message.reply(f'{new_member.first_name}. ' + welcome_text)

    # Ждем 10 секунд
    await asyncio.sleep(300)

    # Удаляем приветственное сообщение
    await welcome_message.delete()
    await message.delete()
