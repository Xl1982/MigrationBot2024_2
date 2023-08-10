import os
import datetime
import pytz
import asyncio
import logging
import aiofiles

from source.data.classes.messages import TextMessagesStorage
from source.bot_init import dp, bot
from .config_chat import config_chat
from source.logger_bot import logger

# Настройка логгирования


async def send_text_messages():
    logger.info('Функция для отправки текстовых сообщений запущена')
    while True:
        # Определите путь к файлу для хранения текстовых сообщений, используя модуль os
        messages_path = os.path.join('source', 'data', 'messages.json')

        # Создайте или работайте с файлом сообщений по указанному пути
        storage = TextMessagesStorage(messages_path)

        chat_id = config_chat['chat_id']
        current_day = datetime.datetime.now(pytz.timezone('Europe/Madrid')).strftime('%A').capitalize()
        # current_day = datetime.datetime.now().strftime('%A').capitalize()

        now = datetime.datetime.now(pytz.timezone('Europe/Madrid')).time()
        # now = datetime.datetime.now().time()
            
        messages_for_current_day = storage.get_messages_for_day(current_day)

        for message_time_str, message_text in messages_for_current_day.items():
            message_time = datetime.datetime.strptime(message_time_str, '%H:%M').time()

            now_hours, now_minutes = now.hour, now.minute
            message_hours, message_minutes = message_time.hour, message_time.minute

            if now_hours == message_hours and now_minutes == message_minutes:
                await bot.send_message(chat_id, message_text)
                
                # Логирование отправки сообщения с русскими буквами
                log_message = f"Sent message: Time={message_time_str}, SentTime={now:%H:%M}, Day={current_day}, Text={message_text}"
                await log_to_file('message_log.txt', log_message)

                await asyncio.sleep(2 * 60)
                
        else:
            await asyncio.sleep(1 * 10)

async def log_to_file(filename, log_message):
    async with aiofiles.open(filename, mode='a', encoding='utf-8') as file:
        await file.write(f"{log_message}\n")


