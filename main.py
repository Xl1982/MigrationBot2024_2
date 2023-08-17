import asyncio
import logging
import os

from aiogram.utils import executor

from source.bot_init import dp, bot
from source.single_chat.youtube import youtube_music
from source.single_chat import start_handler
from source.single_chat import called_taxi
from source.single_chat import send_message_admin
from source.single_chat import meeting_with_translator
from source.single_chat import send_weather_info

from source.single_chat.admin_commands import start, taxi_orders, translator_orders, regulation_of_admins, messages_settings

from source.single_chat.admin_commands import settings_chats

from source.group_chat import delete_replays
from source.group_chat.sending_messages.config_chat import config_chat
from source.group_chat.sending_messages.weather_send_in_group import check_weather_time
from source.group_chat.sending_messages.purchase_currency import send_purchase_currency_notification
from source.group_chat.sending_messages.current_currency import send_currency_notification
from source.group_chat.sending_messages.send_text_messages import send_text_messages
from source.group_chat import welcome_message_timeout
from source.group_chat.sending_messages import weather_send_in_group
from source.group_chat.admin_commands import add_chat_id, ban_users
from source.group_chat.admin_commands import send_messages_in_chats, add_chat_id

from source.market import app

from source.data.classes.add_chat import ChatManager
from source.data.classes.messages import TextMessagesStorage

def make_ever_chat_task():
    path = os.path.join('source', 'data', 'chats.json')
    chat_manager = ChatManager(path)
    chats = chat_manager.get_all_chat_ids()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)    
    for chat_id in chats:
        chat_info = chat_manager.get_chat_data(chat_id)
        if chat_info['send_weather']:
            loop.create_task(check_weather_time(chat_id))
        if chat_info['send_currency']:
            loop.create_task(send_currency_notification(chat_id))
        if chat_info['send_purchase_currency']:
            loop.create_task(send_purchase_currency_notification(chat_id))
        loop.create_task(send_text_messages(chat_id))

            

# Запуск бота
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    make_ever_chat_task()
    
    executor.start_polling(dp, skip_updates=True)
