import asyncio
import multiprocessing

from aiogram.utils import executor

from source.bot_init import dp, bot
from source.single_chat.youtube import youtube_music
from source.single_chat.start_handlers import start_handler
from source.single_chat.taxi import called_taxi
from source.single_chat.interaction_with_admin import send_message_admin
from source.single_chat.interaction_with_translator import meeting_with_translator
from source.single_chat.weather import send_weather_info

from source.single_chat.admin_commands import start, taxi_orders, translator_orders

from source.group_chat.sending_messages.config_chat import config_chat
from source.group_chat.sending_messages.weather_send_in_group import check_weather_time
from source.group_chat.sending_messages.purchase_currency import send_purchase_currency_notification
from source.group_chat.sending_messages.current_currency import send_currency_notification
from source.group_chat.sending_messages.send_text_messages import send_text_message
from source.group_chat.timeouts import welcome_message_timeout
from source.group_chat.sending_messages import weather_send_in_group
from source.group_chat.bans import ban_users
from source.group_chat.timeouts import welcome_message_timeout


# Запуск бота
if __name__ == '__main__':
    # Создание и запуск тасков для выполнения функций check_weather_time и send_currency_notification
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(check_weather_time(chat_id=config_chat['chat_id']))
    loop.create_task(send_currency_notification())
    loop.create_task(send_purchase_currency_notification())
    loop.create_task(send_text_message())

    executor.start_polling(dp, skip_updates=True)