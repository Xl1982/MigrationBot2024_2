from source.bot_init import dp, bot
from source.single_chat.youtube import youtube_music
from source.single_chat.start_handlers import start_handler
from source.single_chat.taxi import called_taxi
from source.single_chat.interaction_with_admin import send_message_admin
from source.single_chat.interaction_with_translator import meeting_with_translator

from source.group_chat.bans import ban_users

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
