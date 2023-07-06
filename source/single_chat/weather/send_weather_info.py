from datetime import datetime

from aiogram import types
from aiogram import filters

from .get_weather_info import get_weather_by_city, get_wind_direction, get_wish
from source.bot_init import dp, bot

# Словарь для перевода дней недели с английского на русский
days_of_week = {
  "Monday": "Понедельник",
  "Tuesday": "Вторник",
  "Wednesday": "Среда",
  "Thursday": "Четверг",
  "Friday": "Пятница",
  "Saturday": "Суббота",
  "Sunday": "Воскресенье"
}


@dp.message_handler(lambda message: message.chat.type == types.ChatType.PRIVATE and message.text == 'Погода')
async def send_weather(message: types.Message):
    # Получаем данные о погоде по названию города
    weather_data = get_weather_by_city("Torrevieja")
    
    # Проверяем наличие ошибки
    if "error" in weather_data:
        # Отправляем пользователю сообщение об ошибке
        await message.reply(f"Произошла ошибка при получении данных о погоде: {weather_data['error']}")
        # Выводим в консоль описание ошибки и название города
        print(f"Error: {weather_data['error']} for city {weather_data['city']}")
    else:
        # Форматируем данные о погоде в красивый текст
        weather_text = (
            f"<b>🌤 Погода в Торревьехе на {datetime.now().strftime('%d.%m.%Y')} ({days_of_week[datetime.now().strftime('%A')]})</b>\n\n"
            f"🌡️ <b>Температура</b>: {weather_data['temp']}°C (ощущается как {weather_data['feels_like']}°C)\n"
            f"⏰ <b>Давление</b>: {weather_data['pressure']} гПа ({round(weather_data['pressure'] * 0.750062, 2)} мм.рт.ст.)\n"
            f"💧 <b>Влажность</b>: {weather_data['humidity']}%\n"
            f"🌬️ <b>Ветер</b>: {weather_data['wind_speed']} м/с ({get_wind_direction(weather_data['wind_deg'])})\n"
            f"☁️ <b>Облачность</b>: {weather_data['clouds']}%\n"
            f"🌅 <b>Восход солнца</b>: {datetime.fromtimestamp(weather_data['sunrise']).strftime('%H:%M')}\n"
            f"🌇 <b>Закат солнца</b>: {datetime.fromtimestamp(weather_data['sunset']).strftime('%H:%M')}\n\n"
            f"<b>{get_wish(weather_data['main'])}</b>"
        )
        # Отправляем пользователю текст с данными о погоде и кнопкой
        await message.reply(
            weather_text,
            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                types.KeyboardButton(
                    text="Назад",
                )
            ),
            parse_mode=types.ParseMode.HTML
        )
