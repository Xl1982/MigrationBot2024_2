import json

from aiogram import types

from source.bot_init import dp, bot
from source.data.classes.add_chat import ChatManager


@dp.message_handler(lambda message: message.chat.type in [types.ChatType.GROUP, types.ChatType.SUPERGROUP],
                    commands=['add_chat'])
async def add_chat_into_config(message: types.Message):
    file_name = "source\data\chats.json"
    chat_manager = ChatManager(file_name)

    # Проверяем, что команда была отправлена администратором чата
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if chat_member.is_chat_admin() or chat_member.status == 'left':
        if message.chat.id not in chat_manager.get_all_chats():
            chat_manager.add_chat(message.chat.id)
            await bot.send_message(message.chat.id, 'Чат добавлен в список для рассылки. Для удаления введите /remove_chat')
        else:
            await bot.send_message(message.chat.id, 'Данный чат уже добавлен. /remove_chat для удаления из списка.')
    else:
        await bot.send_message(message.chat.id, 'Вы не админ.')

@dp.message_handler(lambda message: message.chat.type in [types.ChatType.SUPERGROUP, types.ChatType.GROUP],
                    commands=['remove_chat'])
async def remove_chat_from_config(message: types.Message):
    file_name = "source\data\chats.json"
    chat_manager = ChatManager(file_name)
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if chat_member.is_chat_admin() or chat_member.status == 'left':
        if message.chat.id in chat_manager.get_all_chats():
            chat_manager.remove_chat(message.chat.id)
            await bot.send_message(message.chat.id, 'Данный чат удалён из списка для рассылки. Для добавления введите /add_chat')
        else:
            await bot.send_message(message.chat.id, 'Данного чата нет в списке для рассылки. /add_chat для добавления в список.')
    else:
        await bot.send_message(message.chat.id, 'Вы не админ.')