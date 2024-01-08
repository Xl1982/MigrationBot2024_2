import asyncio
import logging
import os

from aiogram.utils import executor

from source.run_tasks import create_tasks
from source.bot_init import dp, bot
from source.single_chat.youtube import youtube_music
from source.single_chat import start_handler, send_weather_info, called_taxi, send_message_admin, meeting_with_translator

from source.single_chat.admin_commands import start, taxi_orders, translator_orders, regulation_of_admins, messages_settings, spam_filter, settings_chats

from source.group_chat import delete_replays
# from source.group_chat.sending_messages.config_chat import   config_chat
from source.group_chat import welcome_message_timeout
from source.group_chat.sending_messages import weather_send_in_group
from source.group_chat.admin_commands import add_chat_id, ban_users, send_messages_in_chats, add_chat_id

from source.market import app

from source.data.classes.add_chat import ChatManager
from source.data.classes.messages import TextMessagesStorage


logging.basicConfig(
    filename='bot_debug.log',  # Можно изменить имя файла, чтобы отличать от обычного лога
    filemode='a',  # Режим добавления, чтобы не перезаписывать существующие логи
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат логов
    level=logging.DEBUG  # Уровень логирования изменен на DEBUG
)

# Запуск бота
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    create_tasks()

    executor.start_polling(dp, skip_updates=True)

