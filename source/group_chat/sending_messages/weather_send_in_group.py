import datetime
import asyncio
import pytz
import os

from aiogram import types

from source.modules.del_message_timeout import del_message_in_time
from source.group_chat.sending_messages.weather_api import WeatherAPI
from source.bot_init import dp, bot
from source.modules.get_weather_info import get_weather_forecast
from source.logger_bot import logger
from source.config import city_rus, city, WEATHER_API
from source.data.classes.add_chat import ChatManager

from .config_chat import config_chat, times_to_send


api = WeatherAPI(api_key=WEATHER_API)

# Функция для формирования и отправки сообщения с прогнозом погоды
async def send_weather_forecast(chat_id: int, hour=12):
    # Создаем список с доступными временными значениями для выбора
    times = ["09:00", "12:00", "15:00", "18:00", "21:00"]

    # Получаем текущую дату
    current_date = datetime.datetime.now().date()

    # Создаем переменную для хранения текста прогноза погоды
    forecast_message = ""

    # Вызываем функцию для каждого дня, начиная с текущего
    for i in range(5):
        # Вычисляем дату для текущего дня
        target_date = current_date + datetime.timedelta(days=i)
        chat_manager = ChatManager(os.path.join('source', 'data', 'chats.json'))
        chat_info = chat_manager.get_chat_data(str(chat_id))
        weather_chat = chat_info['weather_settings']
        # Проверяем, является ли текущий день первым днем
        is_first_day = (i == 0)
        
        # Получаем прогноз погоды для выбранного дня и времени
        forecast = get_weather_forecast(target_date, datetime.time(hour, 0), city_name=weather_chat['city_en'])
        

        # Проверяем, есть ли доступный прогноз погоды для выбранного дня
        if forecast:
            # Извлекаем информацию о погоде для первого времени из прогноза
            first_time_forecast = forecast[0]

            # Определяем эмодзи в зависимости от состояния погоды
            weather_emoji = ""
            if first_time_forecast['description'] == 'Ясно':
                weather_emoji = "☀️"
            elif first_time_forecast['description'] == 'Дождь':
                weather_emoji = "🌧️"                
            elif first_time_forecast['description'] == 'Снег':
                weather_emoji = "❄️"
            else:
                weather_emoji = "☁️"

            # Формируем текст сообщения на основе шаблона
            if is_first_day:
                forecast = api.get_weather(weather_chat['city_en'])
                # forecast_message += f"{forecast}\n{'-' * 52}\n\n"
                forecast_message += f"{forecast}\n"
            else:
                # Выводим краткую информацию для остальных дней
                simplified_message = f'{"-" * 52}\n'
                simplified_message += f"{target_date.strftime('%d.%m.%Y')}\n"
                simplified_message += f"🌡️ Температура: {first_time_forecast['temperature']}°C\n"
                simplified_message += f"{weather_emoji} Состояние погоды: {first_time_forecast['description']}\n"
                simplified_message += f"💨 Облачность: {first_time_forecast['cloudiness']}%\n"
                # simplified_message += f'{"-" * 52}\n'
                forecast_message += simplified_message 
        else:
            # Если нет доступного прогноза погоды, добавляем сообщение об этом
            forecast_message += f"Нет доступного прогноза погоды для {target_date.strftime('%d.%m.%Y')}\n\n"

    # Отправляем сообщение в чат Telegram
    message = await bot.send_message(chat_id, forecast_message, parse_mode=types.ParseMode.MARKDOWN)
    await del_message_in_time(message)

# Функция для проверки текущего времени
async def check_weather_time(chat_id):
    logger.info('Проверка погоды запущена')
    while config_chat['weather_message']:
        
        target_times = times_to_send['weather_message']

        for target_time in target_times:
            now = datetime.datetime.now(pytz.timezone('Europe/Madrid'))
            # now = datetime.datetime.now()
            current_time = now.time()
            target_time_combine = datetime.datetime.combine(now.date(), target_time)

            time_lower_bound = target_time_combine - datetime.timedelta(minutes=2)
            time_upper_bound = target_time_combine + datetime.timedelta(minutes=2)

            # Проверяем, соответствует ли текущее время заданному времени
            if time_lower_bound.time() < current_time < time_upper_bound.time():
                # Здесь вызываем функцию для отправки прогноза погоды в указанный чат
                await send_weather_forecast(chat_id)

                logger.info('Отправка сообщения с прогнозом погоды')

                await asyncio.sleep(300)
            # Если текущее время не соответствует заданному, ждем 1 минуту и проверяем снова
            await asyncio.sleep(60)
            


# @dp.message_handler(lambda message: message.chat.type in (types.ChatType.GROUP, types.ChatType.SUPERGROUP) and 
#                     message.text == '/weather on')
# async def weather_send_message_on(message: types.Message):
#     config_chat['weather_message'] = True
#     config_chat['chat_id'] = message.chat.id
#     print("Попытка запустить функцию для рассылки погоды")
#     # Запускаем функцию проверки времени с передачей chat_id
#     asyncio.ensure_future(check_weather_time(message.chat.id))

#     await message.answer('Рассылка погоды включена. Ежедневно - в 8:50 утра.')

#     print("Функция выполнилась, погода должна рассылаться")



# @dp.message_handler(lambda message: message.chat.type in (types.ChatType.SUPERGROUP, types.ChatType.GROUP) and
#                     message.text == '/weather off')
# async def weather_send_message_off(message: types.Message):
#     config_chat['weather_message'] = False
#     await message.answer('Рассылка погоды выключена. Используй команду "/weather on"')