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
        now = datetime.datetime.now()
        current_time = now.time()

        for message_time in text_messages:
            # Используйте метод datetime.combine для преобразования времени в дату и время
            lower_bound = datetime.datetime.combine(now.date(), message_time) - datetime.timedelta(minutes=2)
            upper_bound = datetime.datetime.combine(now.date(), message_time) + datetime.timedelta(minutes=2)

            # Сравните текущее время с нижней и верхней границами
            if lower_bound <= now <= upper_bound:
                index = text_messages.index(message_time)
                if index == 0:
                    message_to_send = send_bot_message
                elif index == 1:
                    message_to_send = message

                # Отправка сообщения в чат
                await bot.send_message(config_chat['chat_id'], message_to_send)

                # Логирование отправки сообщения
                logger.info(f"Отправлено текстовое сообщение: {message_to_send}")

        # Ожидание 1 минуты перед проверкой времени снова
        await asyncio.sleep(60)

