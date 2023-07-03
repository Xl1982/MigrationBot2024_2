import logging
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import asyncio
import datetime
from text_message import send_bot_message, message, welcome_message_privat
from config import BOT_TOKEN_GREEN, CHAT_ID_BI, api_key, api_exchange, ADMINS_ID
from keyboards import get_main_keyboard
from states import DownloadState
from pogodaTor import WeatherAPI, weather_text
from xchange010 import CurrencyConverter, exchange_text
from money_sell import Money_sell_converter, money_sell_text
BOT_TOKEN = BOT_TOKEN_GREEN
import time
import pytube
from moviepy.editor import *
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import BOT_TOKEN_GREEN, ADMINS_ID
from keyboards import get_main_keyboard

TOKEN = BOT_TOKEN_GREEN
ADMIN_ID = ADMINS_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
CHAT_ID = CHAT_ID_BI
chat_id_group = CHAT_ID_BI
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async def send_weather_message():
    await bot.send_message(CHAT_ID, weather_text)

async def send_exchange_message():
    await bot.send_message(CHAT_ID, exchange_text)

group_link = "https://t.me/torrevieja_migration"

async def send_text_message():
    await bot.send_message(CHAT_ID, message)

async def send_bot_message2():
    await bot.send_message(CHAT_ID, send_bot_message)

async def send_money_sell():
    await bot.send_message(CHAT_ID, money_sell_text)

# ХЕНДЛЕР КОМАНДЫ  /start
@dp.message_handler(commands=['start'], chat_type=types.ChatType.PRIVATE)
async def start_command(message: types.Message, state: FSMContext):
    await state.reset_state()
    markup = get_main_keyboard()  # Используем функцию для получения клавиатуры
    await message.answer("Привет! Что тебя интересует?", reply_markup=markup)


def download_video(url, output_path):
    youtube = pytube.YouTube(url)
    video = youtube.streams.get_highest_resolution()
    downloaded_video = video.download(output_path)
    return downloaded_video


def convert_to_mp3(video_path, output_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(output_path, bitrate='320k')
    video.close()  # Ensure the video file is closed after use


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print(f"The file {file_path} does not exist")


async def notify_admin(user, file_path):
    username = user.username if user.username else f"id{user.id}"
    await bot.send_message(ADMIN_ID, f"Пользователь {username} скачал файл {file_path}")

# ХЕНДЛЕР ПОЛУЧЕНИЯ ССЫЛКИ НА YOUTUBE
@dp.message_handler(text='Скачать с youtube')
async def download_video_command(message: types.Message, state: FSMContext):
    await DownloadState.WaitingForLink.set()
    markup = get_main_keyboard()  # Используем функцию для получения клавиатуры
    await message.reply("Отправьте ссылку на YouTube видео.", reply_markup=markup)

@dp.message_handler(state=DownloadState.WaitingForLink, content_types=types.ContentTypes.TEXT)
async def handle_youtube_link(message: types.Message, state: FSMContext):
    url = message.text
    if "youtube.com" in url or "youtu.be" in url:
        output_path = download_video(url, "YouTube")
        with open(output_path, 'rb') as video_file:
            await bot.send_video(message.chat.id, video_file, reply_to_message_id=message.message_id)
        await notify_admin(message.from_user, output_path)
        delete_file(output_path)  # Удаляем видео файл после отправки
        await state.finish()
        await start_command(message, state)
    else:
        await message.reply("Пожалуйста, отправьте действительную ссылку на видео YouTube.")




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


#ХЕНДЛЕР ЗАКАЗА ТАКСИ
@dp.message_handler(text='Заказать такси')
async def taxi_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_username = message.from_user.username
    await message.answer(
        "Отлично! Для оформления заказа такси, пожалуйста, укажите следующую информацию:\nОткуда забрать?",
        reply_markup=ReplyKeyboardRemove())  # Убираем клавиатуру после отправки сообщения
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
    markup = get_main_keyboard()  # Используем функцию для получения клавиатуры
    await message.answer("Ваш заказ такси успешно оформлен! Что еще вас интересует?", reply_markup=markup)

    # Сброс состояния пользователя
    await state.finish()

    await message.answer("Ваш заказ такси успешно оформлен!")

# ХЕНДЛЕР ЗАКАЗА ПЕРЕВОДЧИКА
@dp.message_handler(text='Встреча с переводчиком')
async def translator_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_username = message.from_user.username
    await message.answer(
        "Для оформления встречи с переводчиком, пожалуйста, укажите следующую информацию:\n Укажите 📅дату и 🕒время встречи.",
        reply_markup=ReplyKeyboardRemove())
    await state.set_state("ожидание_даты")
    admin_message = f"Новая заявка на встречу с переводчиком!\n\nID: {user_id}\nUsername: @{user_username}"
    await bot.send_message(ADMINS_ID, admin_message)


@dp.message_handler(state="ожидание_даты")
async def process_date(message: types.Message, state: FSMContext):
    date = message.text
    await state.update_data(date=date)
    await message.answer("Укажите место встречи.")
    await state.set_state("ожидание_места")


@dp.message_handler(state="ожидание_места")
async def process_location(message: types.Message, state: FSMContext):
    location = message.text
    await state.update_data(location=location)
    await message.answer("Укажите тематику к сопровождению переводчика (Прописка, полиция)")
    await state.set_state("ожидание_требований")


@dp.message_handler(state="ожидание_требований")
async def process_requirements(message: types.Message, state: FSMContext):
    requirements = message.text
    await state.update_data(requirements=requirements)
    user_data = await state.get_data()

    # Отправка сообщения админу с информацией о встрече с переводчиком
    admin_message = f"Новая заявка на встречу с переводчиком!\n\n" \
                    f"Дата и время: {user_data['date']}\n" \
                    f"Место встречи: {user_data['location']}\n" \
                    f"Требования: {user_data['requirements']}\n"

    await bot.send_message(ADMINS_ID, admin_message)
    # Сброс состояния пользователя
    await state.finish()

    # Возвращение кнопок выбора услуг
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    weather_button = KeyboardButton('Погода')
    exchange_button = KeyboardButton('Курс валют')
    taxi_button = KeyboardButton('Заказать такси')
    translator_button = KeyboardButton('Встреча с переводчиком')
    admin_button = KeyboardButton('Написать админу')
    youtube_button = KeyboardButton('Скачать с youtube')

    markup.add(weather_button, exchange_button, taxi_button, translator_button, admin_button, youtube_button)

    await message.answer("Ваша заявка на встречу с переводчиком успешно отправлена! Что еще вас интересует?",
                         reply_markup=markup)

    # Сброс состояния пользователя
    await state.finish()


###################### ХЕНДЛЕР ОТПРАВКИ ПОГОДЫ И ВАЛЮТЫ ПО РАСПИСАНИЮ
async def send_messages_periodically():
    while True:
        now = datetime.datetime.now()
        if now.hour == 8 and now.minute == 45:
            await send_weather_message()
            print("Отправлено сообщение о погоде")

        elif now.hour == 8 and now.minute == 46:
            await send_exchange_message()
            print("Отправлено сообщение о курсе валют")

        elif now.hour == 8 and now.minute == 47:
            await send_text_message()
            print("Отправлен призывное сообщение")

        elif now.hour == 8 and now.minute == 48:
            await send_bot_message2()
            print("Отправлена реклама бота")

        elif now.hour == 8 and now.minute == 49:
            await send_money_sell()
            print("Отправлена информация о покупке рублей")


        await asyncio.sleep(60)


# ХЕНДЛЕР НАПИСАТЬ АДМИНУ
@dp.message_handler(text='Написать админу')
async def write_to_admin(message: types.Message, state: FSMContext):
    await message.answer("Введите сообщение, которое вы хотите отправить админу.")
    await state.set_state("ожидание_сообщения")


@dp.message_handler(state="ожидание_сообщения")
async def process_message_to_admin(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_username = message.from_user.username
    user_message = message.text

    # Отправка сообщения админу с информацией о пользователе и сообщении
    admin_message = f"Сообщение от пользователя!\n\n" \
                    f"ID: {user_id}\n" \
                    f"Username: @{user_username}\n" \
                    f"Сообщение: {user_message}\n"

    await bot.send_message(ADMINS_ID, admin_message)
    # Сброс состояния пользователя
    await state.finish()

    markup = get_main_keyboard()  # Используем функцию для получения клавиатуры
    await message.answer("Ваше сообщение успешно отправлено админу! Что еще вас интересует?", reply_markup=markup)

    # Сброс состояния пользователя
    await state.finish()

# УДАЛЕНИЕ ПЕРЕСЛАННЫХ СООБШЕНИЙ
@dp.message_handler()
async def antiflood(message: types.Message):
    if message.from_user.id != ADMINS_ID:
        if message.forward_from is not None:
            print("Received forwarded message:", message.text)

            #await message.reply('You cant send forwarded messages.') #разкоменти эту строку если нужно писать сообщения на пересылки
            await message.delete()

# ХЕНДЛЕР ПРИСОЕДИНЕНИЯ НОВОГО ПОЛЬЗОВАТЕЛЯ К ГРУППЕ И ОТВЕТА ЕМУ В ЛИЧКУ
@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def handle_new_members(message: types.Message):
    for new_member in message.new_chat_members:
        try:
            # Обрабатываем каждого нового участника чата
            await process_new_member(new_member)
        except Exception as e:
            # Обработка исключений, если возникла ошибка при обработке нового участника
            print(f"Ошибка при обработке нового участника: {e}")

async def process_new_member(new_member: types.User):
    try:
        # Здесь можно выполнить необходимые действия с новым участником, например, отправить приветственное сообщение
        await bot.send_message(chat_id=chat_id_group, text=f"Поприветствуем нового пользователя!\U0001F44B\nHola, {new_member.first_name}! \U0001F44B\nРасскажи о себе, чем занимаешься, чем интересуешься?"
                                                                                                                      f"Прочти пожалуйста правила группы в закрепе(https://t.me/torrevieja_migration/727)")

        send_run = True
        print("send_run = True")

        if send_run == True:
                time.sleep(600)
                await bot.send_message(chat_id=new_member.id, text=welcome_message_privat)
                print(welcome_message_privat)


    except Exception as e:
        # Обработка исключений, если возникла ошибка при отправке сообщений
        print(f"Ошибка при отправке сообщений новому участнику: {e}")


# ХЕНДЛЕР ПЕРЕХВАТА И ВЫВОДА ПРИВЕТСТВИЯ
@dp.message_handler(content_types=types.ContentType.ANY, is_forwarded=True)
async def handle_forwarded_message(message: types.Message):
    print("Received forwarded message:", message.text)
    await message.answer("Привет! Я перехватил это пересланное сообщение.")



# Запуск бота
if __name__ == '__main__':
    from aiogram import executor

    logging.basicConfig(level=logging.INFO)
    logging.getLogger('aiogram').setLevel(logging.ERROR)
    loop = asyncio.get_event_loop()
    loop.create_task(send_messages_periodically())
    loop.set_debug(True)  # Включаем режим отладки
    executor.start_polling(dp, skip_updates=True)

