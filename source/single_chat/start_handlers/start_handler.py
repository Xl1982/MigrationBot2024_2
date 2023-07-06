from aiogram import types
from aiogram.dispatcher import FSMContext

from database.operations.users import User

from source.single_chat.start_handlers.keyboard import *
from source.bot_init import dp, bot


@dp.message_handler(lambda message: message.text == 'Назад' and message.chat.type == types.ChatType.PRIVATE)
@dp.message_handler(lambda message: message.chat.type == types.ChatType.PRIVATE, commands=['start'])
async def start_work(message: types.Message):
    user = User()
    user.add_user(user_id=message.from_user.id, user_firstname=message.from_user.first_name,
                user_lastname=message.from_user.last_name)
    
    markup = get_main_keyboard()
    await message.answer('Привет! Я бот, который поможет тебе сориетироваться после переезда! '
                        'Нажми на кнопку для выбора интересующей тебя услуги:', reply_markup=markup)
    
