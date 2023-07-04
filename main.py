from source.bot_init import dp, bot
from source.youtube import youtube_music
from source.start_handlers import start_handler
from source.taxi import called_taxi

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
