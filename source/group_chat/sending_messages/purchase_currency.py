import asyncio
import datetime
import pytz
import random

from ...data.classes.money_sell import MoneySellConverter
from source.bot_init import dp, bot
from source.group_chat.sending_messages.config_chat import config_chat
from source.logger_bot import logger
from source.config import ADMIN_LINK
from source.modules.del_message_timeout import del_message_in_time
from source.group_chat.sending_messages.config_chat import times_to_send


async def send_purchase_currency_notification(chat_id):
    target_times = times_to_send['purchase_currency']

    deviation_minutes = [1, 2]  # Время отклонения от графика в минутах
    sleep_minutes = 5  # Время сна после отправки сообщения в минутах
    logger.info('Проверка времени отправки на покупку валюты')
    while config_chat['purchase_message']:
        now = datetime.datetime.now(pytz.timezone('Europe/Madrid'))  # Получение текущего времени в часовом поясе 'Europe/Madrid'
        # now = datetime.datetime.now()
        current_time = now.time()  # Получение объекта time из текущего времени

        # Проверка соответствия текущего времени диапазону вокруг целевого времени с учетом отклонения
        for target_time in target_times:
            target_time_with_deviation = datetime.datetime.combine(now.date(), target_time) + datetime.timedelta(minutes=random.choice(deviation_minutes))
            time_lower_bound = target_time_with_deviation - datetime.timedelta(minutes=2)
            time_upper_bound = target_time_with_deviation + datetime.timedelta(minutes=2)
            if time_lower_bound.time() < current_time < time_upper_bound.time():
                # Создание экземпляра класса CurrencyConverter
                converter = MoneySellConverter()

                # Вызов метода convert_currency для получения текста с обменным курсом
                currency_text, _, _, _ = converter.convert_currency(margin_coefficient=1.1)

                currency_text += f'\nКонтактные данные: {ADMIN_LINK}'

                # Отправка уведомления в чат
                message = await bot.send_message(chat_id, currency_text)

                # Логирование отправки уведомления
                logger.info(f"Отправлено уведомление о покупке валюты: {currency_text}")

                # Переход в режим сна на указанное время
                await asyncio.sleep(sleep_minutes * 60)
                await del_message_in_time(message)

        # Ожидание 1 минуты перед проверкой времени снова
        await asyncio.sleep(60)