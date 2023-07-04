import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


from source.config import MAIN_TOKEN_BOT, ADMINS_ID
from .functions import download_video, download_audio, download_music, is_youtube_link, is_youtube_music_link, check_audio_size, check_video_url, check_video_size
from .states import DownloadState
from ..bot_init import dp, bot
from source.start_handlers.start_handler import start_work


MAX_FILE_SIZE_MB = 50
TOKEN = MAIN_TOKEN_BOT
# ADMIN_ID = ADMINS_ID  # замените на ID администратора

# async def notify_admin(user, file_path):
#     username = user.username if user.username else f"id{user.id}"
#     await bot.send_message(ADMIN_ID, f"Пользователь {username} скачал файл {file_path}")


# Старт ветки с ютубом
@dp.message_handler(lambda message: message.text == 'Скачать с youtube')
async def start_save_youtube(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Назад'))
    await message.reply("Отправь ссылку на трек или видео из ютуба для его загрузки в телеграм.", reply_markup=keyboard)
    await DownloadState.WaitingForLink.set()


# Обработчик сообщений с текстом (получение ссылки на YouTube видео)
@dp.message_handler(state=DownloadState.WaitingForLink)
async def download_content(message: types.Message, state: FSMContext):
    url = message.text

    if is_youtube_music_link(url):
        # Вызываем функцию для загрузки и отправки музыки по ссылке
        result = await download_music(url)
        if result.endswith('.mp3'):
            # Отправляем аудиофайл пользователю
            with open(result, 'rb') as audio:
                await message.answer_audio(audio)
            # Удаляем аудиофайл с диска
            os.remove(result)
        else:
            # Сообщаем об ошибке
            await message.reply(result)
        # Завершаем состояние и переходим к началу работы
        await state.finish()
        await start_save_youtube(message)
    elif is_youtube_link(url):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton('Аудио'))
        keyboard.add(KeyboardButton("Видео"))
        keyboard.add(KeyboardButton('Назад'))

        await message.answer('Ты хочешь скачать видео или аудио-дорожку?', reply_markup=keyboard)
        await state.update_data(url=url)
        await DownloadState.WaitingChoose.set()
    else:
        if message.text == 'Назад':
            await state.finish()
            await start_work(message)
        else:
            await message.reply("Пожалуйста, отправьте действительную ссылку на YouTube видео.")
            return


# Обработчик для выбора аудио или видео
@dp.message_handler(state=DownloadState.WaitingChoose)
async def download_video_or_audio(message: types.Message, state: FSMContext):
    choose = message.text.lower()
    data = await state.get_data()

    if choose == 'аудио':
        # Предполагаем, что ссылка на видео хранится в переменной data['video_url']
        video_url = data.get('url')
        
        # Проверяем ссылку на видео
        error = await check_video_url(video_url)
        if error:
            await message.reply(error)
            await state.finish()
            await start_save_youtube(message)
            return

        # Проверяем размер аудиофайла по ссылке
        error = await check_audio_size(video_url)
        if error:
            await message.reply(error)
            await state.finish()
            await start_save_youtube(message)
            return

        # Загружаем аудиофайл по ссылке
        audio_file_path = await download_audio(video_url)
        if audio_file_path.endswith('.mp3'):  # Если функция вернула путь к файлу, то отправляем его пользователю
            with open(audio_file_path, 'rb') as audio_file:  # Открываем файл в бинарном режиме
                await message.reply_audio(audio_file)  # Отправляем файл как аудиосообщение

            # Удаляем аудиофайл после отправки
            os.remove(audio_file_path)  # Удаляем файл с диска

        # Завершаем состояние и переходим к началу работы
        await state.finish()
        await start_save_youtube(message)

    elif choose == 'видео':
        # Предполагаем, что ссылка на видео хранится в переменной data['video_url']
        video_url = data.get('url')
        
        # Проверяем ссылку на видео
        error = await check_video_url(video_url)
        if error:
            await message.reply(error)
            await state.finish()
            await start_save_youtube(message)            
            return

        # Проверяем размер видеофайла по ссылке
        error = await check_video_size(video_url)
        if error:
            await message.reply(error)
            await state.finish()
            await start_save_youtube(message)
            return

        # Загружаем видеофайл по ссылке
        video_file_path = await download_video(video_url)
        if video_file_path.endswith('.mp4'):  # Если функция вернула путь к файлу, то отправляем его пользователю
            with open(video_file_path, 'rb') as video_file:  # Открываем файл в бинарном режиме
                await message.reply_video(video_file)  # Отправляем файл

            # Удаляем видеофайл после отправки
            os.remove(video_file_path)  # Удаляем файл с диска

        # Завершаем состояние и переходим к началу работы
        await state.finish()
        await start_save_youtube(message)

    else:
        if message.text == 'Назад':
            await state.finish()
            await start_work(message)
            return
        else:
            await message.reply('Выберите один из предложенных вариантов.')




