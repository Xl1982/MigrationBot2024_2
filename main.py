from source.bot_init import dp, bot
from source.youtube import youtube_music

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
