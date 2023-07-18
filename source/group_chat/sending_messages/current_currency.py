import datetime
import asyncio
import pytz
import random

from source.group_chat.sending_messages.config_chat import config_chat, times_to_send
from .money_sell import CurrencyConverter
from source.bot_init import dp, bot
from source.logger_bot import logger

async def send_currency_notification():
    target_times = times_to_send['current_currency']  # Время для отправки уведомления о курсе валют из файла конфигурации

    logger.info('Проверка времени для вывода курса валюты')
    deviation_minutes = [1, 2]  # Время отклонения от графика в минутах
    sleep_minutes = 5  # Время сна после отправки сообщения в минутах

    while config_chat['purchase_message']:
        now = datetime.datetime.now(pytz.timezone('Europe/Madrid'))  # Получение текущего времени в часовом поясе 'Europe/Madrid'
        # now = datetime.datetime.now()
        current_time = now.time()  # Получение объекта time из текущего времени

        # Проверка соответствия текущего времени диапазону вокруг целевого времени с учетом отклонения
        for target_time in target_times:
            target_time_with_deviation = datetime.datetime.combine(now.date(), target_time) + datetime.timedelta(minutes=random.choice(deviation_minutes))
            time_lower_bound = target_time_with_deviation - datetime.timedelta(minutes=2)
            time_upper_bound = target_time_with_deviation + datetime.timedelta(minutes=2)
            if time_lower_bound.time() <= current_time <= time_upper_bound.time():
                # Создание экземпляра класса CurrencyConverter
                converter = CurrencyConverter()

                # Вызов метода convert_currency для получения текста с обменным курсом
                exchange_text, _, _, _ = converter.convert_currency()

                # Отправка уведомления в чат
                await bot.send_message(config_chat['chat_id'], exchange_text)

                # Логирование отправки уведомления
                logger.info(f"Отправлено уведомление о курсе валют: {exchange_text}")

                # Переход в режим сна на указанное время
                # await asyncio.sleep(sleep_minutes * 60)
                await asyncio.sleep(60)

        # Ожидание 1 минуты перед проверкой времени снова
        await asyncio.sleep(60)