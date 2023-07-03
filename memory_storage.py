from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
import datetime
import re
from aiogram.types import KeyboardButtonPollType


from aiogram.utils import executor

# Получение токена бота и идентификатора чата из конфигурационного файла
from config import BOT_TOKEN, CHAT_ID_TORA, api_key, api_exchange, ADMINS_ID

CHAT_ID = CHAT_ID_TORA


# Импорт модулей для работы с погодой и обменным курсом
from pogodaTor import WeatherAPI, weather_text
from xchange010 import CurrencyConverter, exchange_text

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

group_link = "https://t.me/torrevieja_migration"

# Асинхронная функция для отправки текстового  информационного сообщения
async def send_text_message():
    message = f"""

💬 Уважаемые участники!

🙌 Приглашайте своих друзей и знакомых, чтобы расширить наше сообщество и сделать его еще интереснее.

🔗[https://t.me/torrevieja_migration]({group_link})👥

🌟 Наша группа - это место для активного общения, новых знакомств и полезных обменов информацией.

📅 Также, будем рады, если вы будете делиться предстоящими событиями. Если у вас есть информация о концертах, выставках, фестивалях или других интересных мероприятиях, не стесняйтесь сообщать о них в нашей группе. 📣

🤝 Мы приглашаем вас к обмену опытом и знаниями. Если у вас есть вопросы или нужен совет, не стесняйтесь задавать их в нашей группе. 💡

📢 Присоединяйтесь к нам и вместе создадим динамичное и вдохновляющее сообщество! 💪

🎉 Давайте сделаем нашу группу местом, где мы встречаемся, общаемся и узнаем интересные новости! 🌟

#Community #Общение #Мероприятия #Знакомства
"""
    await bot.send_message(CHAT_ID, message)



# ХЕНДЛЕР КОМАНДЫ  /start
@dp.message_handler(commands=['start'], chat_type=types.ChatType.PRIVATE)
async def start_command(message: types.Message, state: FSMContext):
    await state.reset_state()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    weather_button = KeyboardButton('Погода')
    exchange_button = KeyboardButton('Курс валют')
    taxi_button = KeyboardButton('Заказать такси')
    #trans_button = KeyboardButton('Встреча с переводчиком')
    markup.add(weather_button, exchange_button, taxi_button)

    await message.answer("Привет! Что тебя интересует?", reply_markup=markup)


# ХЕНДЛЕР ПОЛЬЗОВАТЕЛЬСКОЙ КНОПКИ ПОГОДА
@dp.message_handler(text='Погода')
async def weather_command(message: types.Message):
    user_id = message.from_user.id
    user_username = message.from_user.username
    city = 'Torrevieja'  # Замените на нужный вам город
    await message.answer(weather_text)
    # Отправка сообщения админу с информацией о просмотре курса валют
    admin_message = f"Новый просмотр погоды!\n\nID: {user_id}\nUsername: @{user_username}"
    await bot.send_message(ADMINS_ID, admin_message)


# ХЕНДЛЕР ПОЛЬЗОВАТЕЛЬСКОЙ КНОПКИ КУРС ВАЛЮТ
@dp.message_handler(text='Курс валют')
async def exchange_command(message: types.Message):
    user_id = message.from_user.id
    user_username = message.from_user.username
    await message.answer(exchange_text)
    # Отправка сообщения админу с информацией о просмотре курса валют
    admin_message = f"Новый просмотр курса валют!\n\nID: {user_id}\nUsername: @{user_username}"
    await bot.send_message(ADMINS_ID, admin_message)


########################### ХЕНДЛЕР ЗАКАЗА ТАКСИ
@dp.message_handler(text='Заказать такси')
async def taxi_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_username = message.from_user.username
    await message.answer("Отлично! Для оформления заказа такси, пожалуйста, укажите следующую информацию:\nОткуда забрать?")
    await state.set_state("ожидание_откуда")
    admin_message = f"Новый заказ такси!\n\nID: {user_id}\nUsername: @{user_username}"
    await bot.send_message(ADMINS_ID, admin_message)


@dp.message_handler(state="ожидание_откуда")
async def process_origin(message: types.Message, state: FSMContext):
    origin = message.text
    await state.update_data(origin=origin)
    await message.answer("Куда поедете?")
    await state.set_state("ожидание_куда")


@dp.message_handler(state="ожидание_куда")
async def process_destination(message: types.Message, state: FSMContext):
    destination = message.text
    await state.update_data(destination=destination)
    await message.answer("Укажите дату и время поездки?")
    await state.set_state("ожидание_время")


@dp.message_handler(state="ожидание_время")
async def process_time(message: types.Message, state: FSMContext):
    time = message.text
    await state.update_data(time=time)
    await message.answer("Введите ваш номер телефона для связи?")
    await state.set_state("ожидание_телефон")


@dp.message_handler(state="ожидание_телефон")
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text
    await state.update_data(phone=phone)
    user_data = await state.get_data()

    # Отправка сообщения админу с информацией о заказе
    admin_message = f"Новый заказ такси!\n\n" \
                    f"Откуда: {user_data['origin']}\n" \
                    f"Куда: {user_data['destination']}\n" \
                    f"Время: {user_data['time']}\n" \
                    f"Телефон: {user_data['phone']}\n"

    await bot.send_message(ADMINS_ID, admin_message)
    # Сброс состояния пользователя
    await state.finish()

    # Возвращение кнопок выбора услуг
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    weather_button = KeyboardButton('Погода')
    exchange_button = KeyboardButton('Курс валют')
    taxi_button = KeyboardButton('Заказать такси')
    markup.add(weather_button, exchange_button, taxi_button)

    await message.answer("Ваш заказ такси успешно оформлен! Что еще вас интересует?", reply_markup=markup)

    # Сброс состояния пользователя
    await state.finish()

    await message.answer("Ваш заказ такси успешно оформлен!")


###################### ХЕНДЛЕР ОТПРАВКИ ПОГОДЫ И ВАЛЮТЫ ПО РАСПИСАНИЮ
async def send_messages_periodically():
    while True:
        now = datetime.datetime.now()
        if now.hour == 11 and now.minute == 00:
            await send_weather_message()
            print("Отправлено сообщение о погоде")
        elif now.hour == 14 and now.minute == 00:
            await send_exchange_message()
            print("Отправлено сообщение о курсе валют")
        elif now.hour == 13 and now.minute == 28:
            await send_text_message()
            print("Отправлен текстовый сообщение")

        await asyncio.sleep(60)



#################### ХЕНДЛЕР ДЛЯ УДАЛЕНИЯ ССЫЛОК
# @dp.message_handler(content_types=types.ContentType.TEXT)
# async def handle_text_message(message: types.Message):
#     # Проверяем, содержит ли сообщение ссылку
#     if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.text):
#         # Отправляем сообщение о запрете ссылок
#         await message.reply("Ссылки запрещены в этом чате!\n"
#                             "Кроме личных страниц в соцсетях!\n"
#                             "Отправьте админу, он разместит https://t.me/Torrevija\n!")
#
#         # Удаляем сообщение с ссылкой
#         await message.delete()




# Точка входа в программу
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_messages_periodically())
    executor.start_polling(dp, loop=loop)
