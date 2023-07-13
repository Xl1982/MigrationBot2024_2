import datetime
import asyncio

from aiogram import types

from source.bot_init import dp, bot
from source.single_chat.weather.get_weather_info import get_weather_forecast


from .config_chat import config_chat


# Функция для формирования и отправки сообщения с прогнозом погоды
async def send_weather_forecast(chat_id: int):
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

        # Проверяем, является ли текущий день первым днем
        is_first_day = (i == 0)

        # Получаем прогноз погоды для выбранного дня и времени
        forecast = get_weather_forecast(target_date, datetime.time(9, 0), city_name='Torrevieja')

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
                # Выводим полную информацию для первого дня
                message = f"🌍 ***{target_date.strftime('%d.%m.%Y')}***\n"
                message += f"{weather_emoji} Погода в городе Torrevieja:\n"
                message += f"🌡️ Температура воздуха: {first_time_forecast['temperature']}°C\n"
                message += f"💧 Влажность: {first_time_forecast['humidity']}%\n"
                message += f"🌬️ Давление: {first_time_forecast['pressure']} мм.рт.ст\n"
                message += f"💨 Скорость ветра: {first_time_forecast['wind_speed']} м/c\n"
                message += f"☁️ Облачность: {first_time_forecast['cloudiness']}%\n"
                message += f"🌅 Время восхода солнца: {first_time_forecast['sunrise'].strftime('%H:%M')}\n"
                message += f"🌇 Время заката солнца: {first_time_forecast['sunset'].strftime('%H:%M')}\n"
                message += f"🌞 Хорошего дня!\n"
                forecast_message += f"{message}{'-' * 52}\n\n"
            else:
                # Выводим краткую информацию для остальных дней
                simplified_message = f'{"-" * 52}\n'
                simplified_message += f"{target_date.strftime('%d.%m.%Y')}\n"
                simplified_message += f"🌡️ Температура: {first_time_forecast['temperature']}°C\n"
                simplified_message += f"{weather_emoji} Состояние погоды: {first_time_forecast['description']}\n"
                simplified_message += f"💨 Облачность: {first_time_forecast['cloudiness']}%\n"
                simplified_message += f'{"-" * 52}\n\n'
                forecast_message += simplified_message 
        else:
            # Если нет доступного прогноза погоды, добавляем сообщение об этом
            forecast_message += f"Нет доступного прогноза погоды для {target_date.strftime('%d.%m.%Y')}\n\n"

    # Отправляем сообщение в чат Telegram
    await bot.send_message(chat_id, forecast_message, parse_mode=types.ParseMode.MARKDOWN)


# Функция для проверки текущего времени
async def check_weather_time(chat_id):
    while config_chat['weather_message']:
        print('Проверка погоды')
        now = datetime.datetime.now()
        target_time_one = datetime.time(8, 50)  # Заданное время (8:50 утра)
        target_time_two = datetime.time(8, 52)

        # Проверяем, соответствует ли текущее время заданному времени
        if target_time_one < now.time() < target_time_two:
            # Здесь вызываем функцию для отправки прогноза погоды в указанный чат
            await send_weather_forecast(chat_id)

            print("Отправка сообщения с прогнозом погоды...")

            await asyncio.sleep(300)
        else:
            # Если текущее время не соответствует заданному, ждем 1 минуту и проверяем снова
            await asyncio.sleep(60)


@dp.message_handler(lambda message: message.chat.type in (types.ChatType.GROUP, types.ChatType.SUPERGROUP) and 
                    message.text == '/weather on')
async def weather_send_message_on(message: types.Message):
    config_chat['weather_message'] = True
    config_chat['chat_id'] = message.chat.id
    print("Попытка запустить функцию для рассылки погоды")
    # Запускаем функцию проверки времени с передачей chat_id
    asyncio.ensure_future(check_weather_time(message.chat.id))

    await message.answer('Рассылка погоды включена. Ежедневно - в 8:50 утра.')

    print("Функция выполнилась, погода должна рассылаться")



@dp.message_handler(lambda message: message.chat.type in (types.ChatType.SUPERGROUP, types.ChatType.GROUP) and
                    message.text == '/weather off')
async def weather_send_message_off(message: types.Message):
    config_chat['weather_message'] = False
    await message.answer('Рассылка погоды выключена. Используй команду "/weather on"')