import asyncio
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor
from config import BOT_TOKEN, CHAT_ID, api_key, api_exchange
from pogodaTor import WeatherAPI, weather_text
from xchange010 import CurrencyConverter, exchange_text
from filters import IsAdmin

now0 = datetime.datetime.now()
print(now0)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class AdminStates(StatesGroup):
    # Состояния администратора
    MAIN_MENU = State()  # Главное меню администратора
    SEND_WEATHER = State()  # Отправка погоды


class UserStates(StatesGroup):
    # Состояния пользователя
    MAIN_MENU = State()  # Главное меню пользователя
    RECEIVE_WEATHER = State()  # Получение погоды


def is_admin(user_id):
    # Функция для определения, является ли пользователь администратором
    # Здесь нужно добавить вашу логику определения администратора
    return False


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    # Определение, является ли пользователь администратором или обычным пользователем
    if is_admin(message.from_user.id):
        await AdminStates.MAIN_MENU.set()
        await message.reply("Вы вошли в главное меню администратора.")
    else:
        await UserStates.MAIN_MENU.set()
        await message.reply("Вы вошли в главное меню пользователя.")


@dp.message_handler(Command("send_weather"), state=AdminStates.MAIN_MENU)
async def send_weather_to_chat(message: types.Message, state: FSMContext):
    weather_api = WeatherAPI(api_key)
    city = 'Torrevieja'
    weather = weather_api.get_weather(city)

    await bot.send_message(CHAT_ID, f"Прогноз погоды для города {city}:\n\n{weather}")
    await message.reply("Прогноз погоды отправлен в чат.")


# Добавьте другие хендлеры и переходы между состояниями для админа и пользователя


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    executor.start_polling(dp, loop=loop)
