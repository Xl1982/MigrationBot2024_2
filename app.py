import asyncio
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor
from config import BOT_TOKEN, CHAT_ID, api_key, api_exchange, ADMINS
from pogodaTor import WeatherAPI, weather_text
from xchange010 import CurrencyConverter, exchange_text
from filters import IsAdmin
from aiogram.types import ReplyKeyboardRemove
from sendmessage010 import SendMessage1
now0 = datetime.datetime.now()

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

@dp.message_handler(IsAdmin(), commands=['start'])
async def start_command(message: types.Message):
    # Определение, является ли пользователь администратором или обычным пользователем
    if await IsAdmin()(message):
        await AdminStates.MAIN_MENU.set()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Кнопка 1')
        button2 = types.KeyboardButton('Кнопка 2')
        button3 = types.KeyboardButton('Кнопка 3')
        button4 = types.KeyboardButton('Кнопка 4')
        button5 = types.KeyboardButton('Кнопка 5')
        keyboard.add(button1, button2, button3, button4, button5)
        await message.reply("Вы вошли в главное меню администратора.", reply_markup=keyboard)
    else:
        await UserStates.MAIN_MENU.set()
        await message.reply("Вы вошли в главное меню пользователя.")

@dp.message_handler(content_types=types.ContentType.TEXT, state=AdminStates.MAIN_MENU)
async def admin_menu_actions(message: types.Message, state: FSMContext):
    if message.text == 'Кнопка 1':
        await message.answer("Вы выбрали кнопку 1.")
        print("gg")
        sender = SendMessage1(BOT_TOKEN, CHAT_ID)




    elif message.text == 'Кнопка 2':
        await message.answer("Вы выбрали кнопку 2.")
    elif message.text == 'Кнопка 3':
        await message.answer("Вы выбрали кнопку 3.")
    elif message.text == 'Кнопка 4':
        await message.answer("Вы выбрали кнопку 4.")
    elif message.text == 'Кнопка 5':
        await message.answer("Вы выбрали кнопку 5.")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    executor.start_polling(dp, loop=loop)
