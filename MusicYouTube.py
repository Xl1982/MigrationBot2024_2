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
TOKEN = BOT_TOKEN_GREEN
ADMIN_ID = ADMINS_ID  # замените на ID администратора

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


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


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Чтобы скачать ВИДЕО или МУЗЫКУ с YouTube. присылай мне ссылку на YouTube видео, и я верну тебе аудио файл.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('Отправить ссылку на YouTube')))


@dp.message_handler(Text('Отправить ссылку на YouTube'), state='*')
async def handle_youtube_button(message: types.Message, state: FSMContext):
    await DownloadState.WaitingForLink.set()
    await message.reply("Отправьте ссылку на YouTube видео.")


@dp.message_handler(state=DownloadState.WaitingForLink, content_types=types.ContentTypes.TEXT)
async def handle_youtube_link(message: types.Message, state: FSMContext):
    url = message.text
    if "music.youtube.com" in url:
        output_path = download_video(url, "YouTube")
        mp3_output_path = output_path[:-4] + ".mp3"  # Заменяем расширение на .mp3
        convert_to_mp3(output_path, mp3_output_path)
        with open(mp3_output_path, 'rb') as audio_file:
            await bot.send_audio(message.chat.id, audio_file, reply_to_message_id=message.message_id)
        await notify_admin(message.from_user, mp3_output_path)
        audio_file.close()  # Ensure the file is closed before deletion
        time.sleep(9)
        delete_file(output_path)  # Удаляем оригинальный видеофайл
        delete_file(mp3_output_path)  # Удаляем mp3 файл после отправки
        await state.finish()
        await start(message)  # Возвращаемся в стартовое состояние
    elif "www.youtube.com" in url:
        output_path = download_video(url, "YouTube")
        with open(output_path, 'rb') as video_file:
            await bot.send_video(message.chat.id, video_file, reply_to_message_id=message.message_id)
        await notify_admin(message.from_user, output_path)
        delete_file(output_path)  # Удаляем видео файл после отправки
        await state.finish()
        await start(message)  # Возвращаемся в стартовое состояние
    else:
        await message.reply("Это не похоже на ссылку YouTube. Пожалуйста, отправьте действительную ссылку на видео или музыку с YouTube.")


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
