from source.bot_init import dp, bot
from source.single_chat.youtube import youtube_music
from source.single_chat.start_handlers import start_handler
from source.single_chat.taxi import called_taxi
from source.single_chat.interaction_with_admin import send_message_admin
from source.single_chat.interaction_with_translator import meeting_with_translator
from source.single_chat.weather import send_weather_info

from source.single_chat.admin_commands import start, taxi_orders

from source.group_chat.timeouts import welcome_message_timeout
from source.group_chat.admin_commands import weather_send_in_group
from source.group_chat.bans import ban_users
from source.group_chat.timeouts import welcome_message_timeout

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
