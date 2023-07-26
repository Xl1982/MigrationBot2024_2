import datetime
import pytz
import asyncio

from source.data.classes.messages import TextMessagesStorage
from source.bot_init import dp, bot
from .config_chat import config_chat
from source.logger_bot import logger



async def send_text_messages():
    storage = TextMessagesStorage(r'source\data\messages.json')

    chat_id = config_chat['chat_id']
    current_day = datetime.datetime.now(pytz.timezone('Europe/Madrid')).strftime('%A').capitalize()
    # current_day = datetime.datetime.now().strftime('%A').capitalize()

    logger.info('Включение функции для отправки текстовых сообщений')

    while config_chat['text_message']:
        now = datetime.datetime.now(pytz.timezone('Europe/Madrid')).time()
        # now = datetime.datetime.now().time()
        # Получаем словарь для текущего дня
        messages_for_current_day = storage.get_messages_for_day(current_day)

        for message_time_str, message_text in messages_for_current_day.items():
            message_time = datetime.datetime.strptime(message_time_str, '%H:%M').time()

            # Проверяем, входит ли текущее время времени отправки в диапазон +- 2 минуты
            start_time = (datetime.datetime.combine(datetime.date.today(), message_time) - datetime.timedelta(minutes=2)).time()
            end_time = (datetime.datetime.combine(datetime.date.today(), message_time) + datetime.timedelta(minutes=2)).time()

            if start_time <= now <= end_time:
                await bot.send_message(chat_id, message_text)
                logger.info(f"Отправлено текстовое сообщение: {message_text}")

                await asyncio.sleep(5 * 60)  # Уход в сон на 5 минут
                
        else:
            await asyncio.sleep(1 * 60)  # Уход в сон на 1 минуту, если сообщение не отправлено



