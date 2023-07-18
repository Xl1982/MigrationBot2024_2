import datetime
import pytz
import asyncio


from .text_message import message, send_bot_message
from source.bot_init import dp, bot
from .config_chat import config_chat, times_to_send
from source.logger_bot import logger


async def send_text_message():
    chat_id = config_chat['chat_id']
    # times_message = список объектов datetime.time()
    times_message = times_to_send['text_messages'] 
    
    logger.info('Проверка времени для отправки текстовых сообщений')

    while config_chat['text_message']:
        now = datetime.datetime.now(pytz.timezone('Europe/Madrid')).time()

        for index, message_time in enumerate(times_message):
            start_time = (datetime.datetime.combine(datetime.date.today(), message_time) - datetime.timedelta(hours=10, minutes=2)).time()
            end_time = (datetime.datetime.combine(datetime.date.today(), message_time) + datetime.timedelta(hours=10, minutes=2)).time()

            if start_time <= now <= end_time:
                if index == 0:
                    message_to_send = send_bot_message
                elif index == 1:
                    message_to_send = message

                await bot.send_message(chat_id, message_to_send)
                logger.info(f"Отправлено текстовое сообщение: {message_to_send}")
                logger.info('Проверка времени для отправки текстовых сообщений')

                # await asyncio.sleep(5 * 60)  # Уход в сон на 5 минут
                await asyncio.sleep(60)

        else:
            await asyncio.sleep(1 * 60)  # Уход в сон на 1 минуту, если сообщение не отправлено



