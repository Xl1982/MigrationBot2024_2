import json
import asyncio
import os

from aiogram import types

from source.run_tasks import create_tasks, tasks, new_tasks
from source.bot_init import dp, bot
from source.data.classes.add_chat import ChatManager


# При добавлении чата в json
@dp.message_handler(lambda message: message.chat.type in [types.ChatType.GROUP, types.ChatType.SUPERGROUP],
                    commands=['add_chat'])
async def add_chat_into_config(message: types.Message):
    file_name = os.path.join("source", "data", "chats.json")
    chat_manager = ChatManager(file_name)

    # Проверяем, что команда была отправлена администратором чата
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if chat_member.is_chat_admin() or chat_member.status == 'left':
        if str(message.chat.id) not in chat_manager.get_all_chat_ids():
            chat_name = message.chat.title  # Используем название чата как название для ChatManager
            chat_manager.add_chat(str(message.chat.id), chat_name)
            bot_message = await bot.send_message(message.chat.id, 'Чат добавлен в список чатов для управления. Для удаления введите /remove_chat')
            new_tasks(chat_id=message.chat.id)
        else:
            bot_message = await bot.send_message(message.chat.id, 'Данный чат уже добавлен для настроек. /remove_chat для удаления из списка.')
    else:
        bot_message = await bot.send_message(message.chat.id, 'Вы не админ.')
    await asyncio.sleep(10)
    await message.delete()
    await bot_message.delete()

# При удалении чата из файла json
@dp.message_handler(lambda message: message.chat.type in [types.ChatType.SUPERGROUP, types.ChatType.GROUP],
                    commands=['remove_chat'])
async def remove_chat_from_config(message: types.Message):
    # Путь и экземпляр менеджера
    file_name = os.path.join("source", "data", "chats.json")
    chat_manager = ChatManager(file_name)
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    # Если админ или от лица чата
    if chat_member.is_chat_admin() or chat_member.status == 'left':
        if str(message.chat.id) in chat_manager.get_all_chat_ids():
            # Удаляем, запускаем таски вновь (чтоб убедиться что их больше нет)
            chat_manager.remove_chat(str(message.chat.id))
            bot_message = await bot.send_message(message.chat.id, 'Данный чат удалён из списка чатов для управления. Для добавления введите /add_chat')
            new_tasks(chat_id=message.chat.id)
        else:
            # Если чата нет в рассылке
            bot_message = await bot.send_message(message.chat.id, 'Данный чат не добавлен для настроек. /add_chat для добавления в список.')
    else:
        bot_message = await bot.send_message(message.chat.id, 'Вы не админ.')
    await asyncio.sleep(10)
    await message.delete()
    await bot_message.delete()