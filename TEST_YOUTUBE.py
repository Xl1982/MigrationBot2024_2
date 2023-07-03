import os
import time

import pytube
from moviepy.editor import *
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import BOT_TOKEN_GREEN, ADMINS_ID
from keyboards import get_main_keyboard

TOKEN = BOT_TOKEN_GREEN
ADMIN_ID = ADMINS_ID  # замените на ID администратора

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)



@dp.message_handler(commands=['start'], chat_type=types.ChatType.PRIVATE)
async def start_command(message: types.Message, state: FSMContext):
    await state.reset_state()
    markup = get_main_keyboard()  # Используем функцию для получения клавиатуры
    await message.answer("Привет! Что тебя интересует?", reply_markup=markup)

#youtube
class DownloadState(StatesGroup):
    WaitingForLink = State()


def download_video(url, output_path):
    youtube = pytube.YouTube(url)
    video = youtube.streams.get_highest_resolution()
    downloaded_video = video.download(output_path)
    return downloaded_video


def convert_to_mp3(video_path, output_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(output_path, bitrate='320k')
    video.close()  # Ensure the video file is closed after use


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print(f"The file {file_path} does not exist")


async def notify_admin(user, file_path):
    username = user.username if user.username else f"id{user.id}"
    await bot.send_message(ADMIN_ID, f"Пользователь {username} скачал файл {file_path}")

# ХЕНДЛЕР ПОЛУЧЕНИЯ ССЫЛКИ НА YOUTUBE
@dp.message_handler(text='Скачать с youtube')
async def download_video_command(message: types.Message, state: FSMContext):
    await DownloadState.WaitingForLink.set()
    markup = get_main_keyboard()  # Используем функцию для получения клавиатуры

    await message.reply("Отправьте ссылку на YouTube видео.", reply_markup=markup)

@dp.message_handler(state=DownloadState.WaitingForLink, content_types=types.ContentTypes.TEXT)
async def handle_youtube_link(message: types.Message, state: FSMContext):
    url = message.text
    if "youtube.com" in url or "youtu.be" in url:
        output_path = download_video(url, "YouTube")
        with open(output_path, 'rb') as video_file:
            await bot.send_video(message.chat.id, video_file, reply_to_message_id=message.message_id)
        await notify_admin(message.from_user, output_path)
        delete_file(output_path)  # Удаляем видео файл после отправки
        await state.finish()
        await start_command(message, state)
    else:
        await message.reply("Пожалуйста, отправьте действительную ссылку на видео YouTube.")


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
