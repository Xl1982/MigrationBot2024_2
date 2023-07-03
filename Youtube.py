import pytube
from aiogram import Bot, Dispatcher, types
from config import BOT_TOKEN_GREEN

TOKEN = BOT_TOKEN_GREEN
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

def download_video(url, output_path):
    youtube = pytube.YouTube(url)
    video = youtube.streams.get_highest_resolution()
    downloaded_video = video.download(output_path)
    return downloaded_video

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Присылайте мне ссылку на YouTube видео, и я верну вам это видео.")

@dp.message_handler()
async def echo(message: types.Message):
    url = message.text
    if "youtube.com" in url:
        output_path = download_video(url, "YouTube")
        with open(output_path, 'rb') as video_file:
            await bot.send_video(message.chat.id, video_file)
    else:
        await message.reply("Это не похоже на ссылку YouTube. Пожалуйста, отправьте действительную ссылку на видео с YouTube.")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
