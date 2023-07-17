from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text
from aiogram.types import ContentType, ReplyKeyboardMarkup, KeyboardButton
import asyncio
import datetime
import re

from aiogram.utils import executor

# Получение токена бота и идентификатора чата из конфигурационного файла
from source.config import BOT_TOKEN, CHAT_ID_TORA, api_key, api_exchange, ADMINS_ID

CHAT_ID = CHAT_ID_TORA

# Импорт модулей для работы с погодой и обменным курсом
from source.weather.pogodaTor import WeatherAPI, weather_text
from source.main_handlers.xchange010 import CurrencyConverter, exchange_text

# Создание экземпляра бота
bot = Bot(token=BOT_TOKEN)
# Создание экземпляра диспетчера для обработки сообщений
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Асинхронная функция для отправки сообщения о погоде
async def send_weather_message():
    await bot.send_message(CHAT_ID, weather_text)


# Асинхронная функция для отправки сообщения об обменном курсе
async def send_exchange_message():
    await bot.send_message(CHAT_ID, exchange_text)


# Хэндлер для команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message, state: FSMContext):
    await state.reset_state()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    weather_button = KeyboardButton('Погода')
    exchange_button = KeyboardButton('Курс валют')
    taxi_button = KeyboardButton('Заказать такси')
    markup.add(weather_button, exchange_button, taxi_button)

    await message.answer("Привет! Что тебя интересует?", reply_markup=markup)


# Хэндлер для кнопки "Погода"
@dp.message_handler(Text('Погода'))
async def weather_command(message: types.Message):
    await message.answer(weather_text)


# Хэндлер для кнопки "Курс валют"
@dp.message_handler(Text('Курс валют'))
async def exchange_command(message: types.Message):
    await message.answer(exchange_text)


# Хэндлер для кнопки "Заказать такси"
@dp.message_handler(Text('Заказать такси'), content_types=ContentType.LOCATION, chat_type=types.ChatType.PRIVATE)
async def taxi_command(message: types.Message, state: FSMContext):
    await message.answer("Отлично! Для оформления заказа такси, пожалуйста, укажите следующую информацию:\n"
                         "Откуда забрать?")
    await state.set_state("ожидание_откуда")


@dp.message_handler(content_types=ContentType.LOCATION, state="ожидание_откуда", chat_type=types.ChatType.PRIVATE)
async def process_origin(message: types.Message, state: FSMContext):
    location = message.location
    await state.update_data(location=location)
    await message.answer("Куда поедете?")
    await state.set_state("ожидание_куда")


@dp.message_handler(state="ожидание_куда", chat_type=types.ChatType.PRIVATE)
async def process_destination(message: types.Message, state: FSMContext):
    destination = message.text
    await state.update_data(destination=destination)
    await message.answer("Укажите время поездки?")
    await state.set_state("ожидание_время")


@dp.message_handler(state="ожидание_время", chat_type=types.ChatType.PRIVATE)
async def process_time(message: types.Message, state: FSMContext):
    time = message.text
    await state.update_data(time=time)
    await message.answer("Введите ваш номер телефона для связи?")
    await state.set_state("ожидание_телефон")


@dp.message_handler(state="ожидание_телефон", chat_type=types.ChatType.PRIVATE)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text
    await state.update_data(phone=phone)
    user_data = await state.get_data()

    # Отправка сообщения админу с информацией о заказе
    admin_message = f"Новый заказ такси!\n\n" \
                    f"Откуда: {user_data.get('location')}\n" \
                    f"Куда: {user_data.get('destination')}\n" \
                    f"Время: {user_data.get('time')}\n" \
                    f"Телефон: {user_data.get('phone')}\n"

    await bot.send_message(ADMINS_ID, admin_message)

    # Сброс состояния пользователя
    await state.finish()

    await message.answer("Ваш заказ такси успешно оформлен!")


# Асинхронная функция для периодической отправки сообщений
async def send_messages_periodically():
    while True:
        now = datetime.datetime.now()
        if now.hour == 10 and now.minute == 0:
            await send_weather_message()
            print("Отправлено сообщение о погоде")
        elif now.hour == 11 and now.minute == 0:
            await send_exchange_message()
            print("Отправлено сообщение о курсе валют")
        await asyncio.sleep(60)


# Точка входа в программу
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_messages_periodically())
    executor.start_polling(dp, loop=loop)
