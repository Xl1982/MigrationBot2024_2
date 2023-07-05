from aiogram import types
from aiogram.dispatcher import FSMContext

from source.single_chat.start_handlers.keyboard import *
from source.bot_init import dp, bot


@dp.message_handler(lambda message: message.text == 'Назад')
@dp.message_handler(commands=['start'])
async def start_work(message: types.Message):
    markup = get_main_keyboard()
    await message.answer('Привет! Я бот, который поможет тебе сориетироваться после переезда! '
                        'Нажми на кнопку для выбора интересующей тебя услуги:', reply_markup=markup)
    
