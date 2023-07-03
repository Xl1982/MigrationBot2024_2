from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from source.config import MAIN_TOKEN_BOT, ADMINS_ID
from .functions import download_video, download_audio, download_music, is_youtube_link, is_youtube_music_link
from .states import DownloadState
from ..bot_init import dp, bot

TOKEN = MAIN_TOKEN_BOT
# ADMIN_ID = ADMINS_ID  # замените на ID администратора

# async def notify_admin(user, file_path):
#     username = user.username if user.username else f"id{user.id}"
#     await bot.send_message(ADMIN_ID, f"Пользователь {username} скачал файл {file_path}")


# Обработчик команды /start
@dp.message_handler(commands=['youtube'])
async def start_save_youtube(message: types.Message):
    await message.reply("Отправь ссылку на трек или видео для его загрузки в телеграм.", reply_markup=ReplyKeyboardRemove())
    await DownloadState.WaitingForLink.set()


# Обработчик сообщений с текстом (получение ссылки на YouTube видео)
@dp.message_handler(state=DownloadState.WaitingForLink)
async def download_content(message: types.Message, state: FSMContext):
    url = message.text

    if is_youtube_music_link(url):
        await download_music(url, message.chat.id)
        await state.finish()
        await start_save_youtube(message)
    elif is_youtube_link(url):
        keyboard = ReplyKeyboardMarkup()
        keyboard.add(KeyboardButton('Аудио'))
        keyboard.add(KeyboardButton("Видео"))

        await message.answer('Ты хочешь скачать видео или аудио-дорожку?', reply_markup=keyboard)
        await state.update_data(url=url)
        await DownloadState.WaitingChoose.set()
        # await download_video(url, message.chat.id)
        # await state.finish()
        # await start(message)
    else:
        await message.reply("Пожалуйста, отправьте действительную ссылку на YouTube видео.")
        return

@dp.message_handler(state=DownloadState.WaitingChoose)
async def download_video_or_audio(message: types.Message, state: FSMContext):
    choose = message.text.lower()
    data = await state.get_data()
    if choose == 'аудио':
        await download_audio(data['url'], message.chat.id)
        await state.finish()
        await start_save_youtube(message)
    elif choose == 'видео':
        await download_video(data['url'], message.chat.id)
        await state.finish()
        await start_save_youtube(message)
    else:
        await message.reply('Выберите один из предложенных вариантов.')
        return


