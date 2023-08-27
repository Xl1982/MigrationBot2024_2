import os
import datetime
import pytz
import asyncio
import logging
import aiofiles

from aiogram import types

from source.data.classes.messages import TextMessagesStorage
from source.bot_init import dp, bot
from source.logger_bot import logger

# Настройка логгирования


async def send_text_messages(chat_id):
    logger.info('Функция для отправки текстовых сообщений запущена')
    while True:
        # Определите путь к файлу для хранения текстовых сообщений, используя модуль os
        messages_path = os.path.join('source', 'data', 'messages.json')

        # Создайте или работайте с файлом сообщений по указанному пути
        storage = TextMessagesStorage(messages_path)

        current_day = datetime.datetime.now(pytz.timezone('Europe/Madrid')).strftime('%A').capitalize()
        # current_day = datetime.datetime.now().strftime('%A').capitalize()

        now = datetime.datetime.now(pytz.timezone('Europe/Madrid')).time()
        # now = datetime.datetime.now().time()

        messages_for_current_day = storage.get_messages_for_day(chat_id, current_day)

        for info_message in messages_for_current_day:
            message_time = datetime.datetime.strptime(info_message['time_sent'], '%H:%M').time()
            now_hours, now_minutes = now.hour, now.minute

            message_hours, message_minutes = message_time.hour, message_time.minute

            if now_hours == message_hours and now_minutes == message_minutes:
                media_group = []
                photos = info_message['photos']
                videos = info_message['videos']

                if photos:
                    for i, photo_id in enumerate(photos):
                        caption = info_message['text'] if i == 0 else None
                        media_group.append(types.InputMediaPhoto(media=photo_id, caption=caption))

                if videos:
                    for i, video_id in enumerate(videos):
                        if not photos and i == 0:
                            caption = info_message['text']
                        else:
                            caption = None
                        media_group.append(types.InputMediaVideo(media=video_id, caption=caption))

                if media_group:
                    await bot.send_media_group(chat_id, media=media_group)
                else:
                    await bot.send_message(chat_id, info_message['text'])
                
                log_message = f"Sent message: Time={message_time}, SentTime={now:%H:%M}, Day={current_day}, Text={info_message['text']}"
                await log_to_file('message_log.txt', log_message)

        await asyncio.sleep(60 * 1)


async def log_to_file(filename, log_message):
    async with aiofiles.open(filename, mode='a', encoding='utf-8') as file:
        await file.write(f"{log_message}\n")


