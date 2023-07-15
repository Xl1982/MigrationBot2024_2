import datetime
import pytz
import asyncio

from .text_message import message, send_bot_message
from source.bot_init import dp, bot
from .config_chat import config_chat, times_to_send
from source.logger_bot import logger


async def send_text_message():
    text_messages = times_to_send['text_messages']  # Список временных значений для сообщений из файла конфигурации
    
    logger.info('Проверка времени для вывода текстового сообщения')
    while config_chat['text_message']:
        now = datetime.datetime.now(pytz.timezone('Europe/Madrid'))  # Получение текущего времени в часовом поясе 'Europe/Madrid'
        current_time = now.time()

        if current_time in text_messages:
            index = text_messages.index(current_time)
            if index == 0:
                message = send_bot_message
            elif index == 1:
                message = message

            # Отправка сообщения в чат
            await bot.send_message(config_chat['chat_id'], message)

            # Логирование отправки сообщения
            logger.info(f"Отправлено текстовое сообщение: {message}")

        # Ожидание 1 минуты перед проверкой времени снова
        await asyncio.sleep(60)


