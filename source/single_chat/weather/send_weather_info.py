from datetime import datetime, timedelta

from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup

from source.single_chat.start_handlers.start_handler import old_user_hello
from .get_weather_info import get_weather_forecast
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

class WeatherStates(StatesGroup):
    waiting_date = State()
    waiting_time = State()


def get_day_button_text(day):
    month_names = {
        "January": "января",
        "February": "февраля",
        "March": "марта",
        "April": "апреля",
        "May": "мая",
        "June": "июня",
        "July": "июля",
        "August": "августа",
        "September": "сентября",
        "October": "октября",
        "November": "ноября",
        "December": "декабря",
    }

    # Определяем текст кнопки на основе дня
    if day == datetime.now().date():
        return "Сегодня"
    elif day == datetime.now().date() + timedelta(days=1):
        return "Завтра"
    elif day == datetime.now().date() + timedelta(days=2):
        return "Послезавтра"
    else:
        return f"{day.day} {month_names[day.strftime('%B')]}"



@dp.message_handler(lambda message: message.chat.type == types.ChatType.PRIVATE and message.text == 'Погода')
async def choose_weather_day(message: types.Message):
    # Определяем текущую дату
    today = datetime.now().date()

    # Создаем список с доступными днями для выбора (5 дней, начиная от текущего дня)
    available_days = [today + timedelta(days=i) for i in range(5)]

    # Создаем список с кнопками для каждого доступного дня
    buttons = [
        types.InlineKeyboardButton(text=get_day_button_text(day), callback_data=f"day_{day.strftime('%Y-%m-%d')}")
        for day in available_days
    ]
    # Создаем inline keyboard из списка кнопок
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    keyboard.add(types.InlineKeyboardButton('Выход', callback_data='exit'))

    # Отправляем сообщение с inline keyboard и просим пользователя выбрать день для прогноза погоды
    await message.answer("Выберите день для прогноза погоды:", reply_markup=keyboard)
    await WeatherStates.waiting_date.set()


@dp.callback_query_handler(lambda query: query.message.chat.type == types.ChatType.PRIVATE and query.data.startswith("day_"),
                           state=WeatherStates.waiting_date)
async def handle_weather_day(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    
    # Получаем выбранный день из callback_query
    selected_day = callback_query.data.split("_")[1]

    # Определяем целевую дату на основе выбранного дня
    target_date = datetime.strptime(selected_day, "%Y-%m-%d").date()

    await state.update_data(selected_day=target_date)

    # Создаем список с доступными временными значениями для выбора
    times = ["09:00", "12:00", "15:00", "18:00", "21:00"]

    # Создаем список с кнопками для каждого доступного времени
    buttons = [types.InlineKeyboardButton(text=time, callback_data=f"time_{time}") for time in times]

    # Создаем inline keyboard из списка кнопок
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    keyboard.add(types.InlineKeyboardButton('Выход', callback_data='exit'))

    # Отправляем сообщение с inline keyboard и просим пользователя выбрать время прогноза погоды
    await bot.send_message(callback_query.from_user.id, "Выберите время для прогноза погоды:", reply_markup=keyboard)
    await WeatherStates.waiting_time.set()
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)


@dp.callback_query_handler(lambda query: query.message.chat.type == types.ChatType.PRIVATE and query.data.startswith("time_"),
                           state=WeatherStates.waiting_time)
async def handle_weather_time(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()

    data = await state.get_data()
    selected_day = data['selected_day']
    selected_time = callback_query.data.split("_")[1]

    target_time = datetime.strptime(selected_time, "%H:%M").time()

    try:
        forecast = get_weather_forecast(selected_day, target_time)[0]
    except IndexError:
        await callback_query.message.answer('Нельзя просмотреть прогноз на прошеднее время')
        await state.finish()
        await old_user_hello(callback_query, state)
        return

    if forecast:
        response = f"Прогноз погоды для {selected_day.strftime('%d-%m-%Y')} {target_time.strftime('%H:%M')}:\n"
        response += f"🌍 Город: Торревьеха\n"
        response += f"🌡️ <b>Температура:</b> {forecast['temperature']}°C\n"
        response += f"💧 <b>Влажность:</b> {forecast['humidity']}%\n"
        response += f"💨 <b>Скорость ветра:</b> {forecast['wind_speed']} м/с\n"
        response += f"🧭 <b>Направление ветра:</b> {forecast['wind_direction']}\n"
        response += f"⛅ <b>Давление:</b> {forecast['pressure']} гПа\n"
        response += f"🌫️ <b>Видимость:</b> {forecast['visibility']} м"

        # Добавляем смайлы и выделение жирным шрифтом
        # response = f"⏰ {selected_time} - {forecast['wish']} ⏰\n\n" + response

        await bot.send_message(callback_query.from_user.id, response, parse_mode="HTML")
        await state.finish()
        await old_user_hello(callback_query, state)
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    else:
        await bot.send_message(callback_query.from_user.id, "Прогноз погоды для указанного времени недоступен.")
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)



