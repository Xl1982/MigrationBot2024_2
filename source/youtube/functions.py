import yt_dlp
import os
import re
import asyncio

from aiogram.types import ReplyKeyboardRemove
from moviepy.editor import *

from source.bot_init import dp, bot

ADMIN_ID = 1387633357

# Функция для обновления прогресса загрузки или конвертации
# async def update_progress(data, chat_id, message_id):
#     if data['status'] == 'downloading': # Если идет загрузка
#         percent = data['_percent_str'] # Процент загрузки в виде строки
#         speed = data['_speed_str'] # Скорость загрузки в виде строки
#         await bot.edit_message_text(f"Загружается {percent} со скоростью {speed}", chat_id, message_id) # Редактируем сообщение с прогрессом (нужно сохранить message_id при первом выводе)
#     elif data['status'] == 'finished': # Если загрузка завершена
#         await bot.edit_message_text("Загрузка завершена, идет конвертация...", chat_id, message_id) # Редактируем сообщение с прогрессом


async def download_music(url, chat_id):
    try:
        # Отправляем сообщение с начальным прогрессом
        # message = await bot.send_message(chat_id, "Загружается 0% со скоростью 0 КБ/с")
        # Сохраняем message_id
        # message_id = message.message_id
        await bot.send_message(chat_id=chat_id, text='Скачиваю музыку, подождите...')
        # Настройки загрузки
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            # Добавляем прогресс-хук для отслеживания состояния загрузки
            # 'progress_hooks': [lambda d: asyncio.create_task(update_progress(d, chat_id, message_id))],
        }
        # Сохранение и отправка
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False) # Сначала получаем информацию о видео без загрузки
            audio_size = info_dict['filesize'] # Размер аудио в байтах
            if audio_size > 50 * 1024 * 1024: # Если больше 50 МБ
                await bot.send_message(chat_id, f"Файл слишком большой ({audio_size / 1024 / 1024:.2f} МБ), попробуйте найти вариант меньше длительностью."
                                       " Максимальный размер файла - 50 МБ")
                return # Прерываем функцию
            else: # Иначе продолжаем загрузку
                ydl.process_info(info_dict) # Загружаем видео по информации
                audio_path = ydl.prepare_filename(info_dict)
                # Заменяем расширение webm на mp3
                audio_path = audio_path.replace('.webm', '.mp3')
                await bot.send_audio(chat_id, audio=open(audio_path, 'rb'))
                # Удаляем трек после отправки
                os.remove(audio_path)
    except Exception as e:
        await bot.send_message(chat_id, f"Произошла ошибка при скачивании музыки: {e}")


async def download_audio(url, chat_id):
    try:
        # Отправляем сообщение с начальным прогрессом
        # message = await bot.send_message(chat_id, "Загружается 0% со скоростью 0 КБ/с")
        # Сохраняем message_id
        # message_id = message.message_id
        await bot.send_message(chat_id=chat_id, text='Сохраняю аудио-дорожку, подожди...')
        # Настройки загрузки
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            # Добавляем прогресс-хук для отслеживания состояния загрузки
            # 'progress_hooks': [lambda d: asyncio.create_task(update_progress(d, chat_id, message_id))],
        }
        # Сохранение и отправка
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True) # Загружаем видео сразу
            audio_path = ydl.prepare_filename(info_dict)
            # Заменяем расширение webm на mp3
            audio_path = audio_path.replace('.webm', '.mp3')
            audio_size = os.path.getsize(audio_path) # Получаем размер аудио в байтах
            if audio_size > 50 * 1024 * 1024: # Если больше 50 МБ
                await bot.send_message(chat_id, f"Файл слишком большой ({audio_size / 1024 / 1024:.2f} МБ), попробуйте найти вариант меньше длительностью."
                                       " Максимальный размер файла - 50 МБ")
                os.remove(audio_path) # Удаляем трек после проверки
                return # Прерываем функцию
            else: # Иначе продолжаем отправку
                await bot.send_audio(chat_id, audio=open(audio_path, 'rb')) # Отправляем файл, а не месторасположение
                os.remove(audio_path) # Удаляем трек после отправки
    except Exception as e:
        await bot.send_message(chat_id, f"Произошла ошибка при сохранении аудио-дорожки: {e}")



async def download_video(url, chat_id):
    try:
        # Отправляем сообщение с начальным прогрессом
        # message = await bot.send_message(chat_id, "Загружается 0% со скоростью 0 КБ/с")
        # # Сохраняем message_id
        # message_id = message.message_id
        await bot.send_message(chat_id=chat_id, text='Скачиваю видео, подождите...', reply_markup=ReplyKeyboardRemove())
        ydl_opts = {
            "format": "bestvideo+bestaudio",
            "outtmpl": "%(id)s.%(ext)s",
            "noplaylist": True,
            # Добавляем пост-процессор для конвертации видео в mp4
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4"
            }],
            # Добавляем прогресс-хук для отслеживания состояния загрузки или конвертации
            # 'progress_hooks': [lambda d: asyncio.create_task(update_progress(d, chat_id, message_id))],
        }
        # Используем yt_dlp для скачивания видео
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Получаем информацию о видео без загрузки
            info = ydl.extract_info(url, download=False)
            # Получаем идентификатор и расширение видео
            video_id = info["id"]
            video_ext = info["ext"]
            # Получаем примерный размер видео в байтах
            video_size_approx = info["filesize_approx"]
            if video_size_approx > 50 * 1024 * 1024: # Если больше 50 МБ
                await bot.send_message(chat_id, f"Видео слишком большое ({video_size_approx / 1024 / 1024:.2f} МБ),"
                                            " попробуйте найти вариант меньше длительностью или разрешением. Максимальный размер файла - 50МБ")
                return # Прерываем функцию
            else: # Иначе продолжаем загрузку
                ydl.process_info(info) # Загружаем видео по информации
                # Заменяем расширение webm на mp4
                video_path = f"{video_id}.{video_ext}".replace(".webm", ".mp4")
                # Открываем файл видео
                with open(video_path, "rb") as f:
                    # Проверяем реальный размер видео в байтах
                    video_size = os.path.getsize(video_path)
                    if video_size > 50 * 1024 * 1024: # Если больше 50 МБ
                        await bot.send_message(chat_id, f"Видео слишком большое ({video_size / 1024 / 1024:.2f} МБ),"
                                            " попробуйте найти вариант меньше длительностью или разрешением. Максимальный размер файла - 50 МБ")
                        f.close()
                        os.remove(video_path) # Удаляем видео
                        return # Прерываем функцию
                    else: # Иначе отправляем видео в чат
                        await bot.send_video(chat_id, f)
                        # Удаляем видео после отправки
                        f.close()
                        os.remove(video_path)
    except Exception as e:
        print(f'Ошибка {e}')


def is_youtube_link(url):
    # Регулярное выражение для проверки, что ссылка принадлежит YouTube
    youtube_pattern = r"(?:https?://)?(?:www\.)?(?:youtube\.com|youtu\.be)"

    # Проверяем, соответствует ли ссылка YouTube
    if re.match(youtube_pattern, url):
        return True
    else:
        return False

def is_youtube_music_link(url):
    # Регулярное выражение для проверки, что ссылка принадлежит YouTube Music
    youtube_music_pattern = r"(?:https?://)?(?:www\.)?(?:music\.youtube\.com)"

    # Проверяем, соответствует ли ссылка YouTube Music
    if re.match(youtube_music_pattern, url):
        return True
    else:
        return False
