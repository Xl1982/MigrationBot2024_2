from aiogram import types
from aiogram.dispatcher import FSMContext

from database.operations.users import User

from source.group_chat.sending_messages.money_sell import CurrencyConverter
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
    

@dp.callback_query_handler(lambda c: c.data == 'exit', state='*')
async def old_user_hello(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    markup = get_main_keyboard()
    await callback_query.answer()
    await callback_query.message.answer('Выбери действие нажав на кнопку на клавиатуре:', reply_markup=markup)


@dp.message_handler(lambda message: message.text == 'Расписание автобусов', chat_type=types.ChatType.PRIVATE)
async def send_bus_timetable(message: types.Message):
    link_to_timetable = 'https://telegra.ph/Raspisanie-avtobusov-v-gorode-Terreveha-07-10'

    await message.answer(f'Расписание автобусов есть в данной статье: {link_to_timetable}')


@dp.message_handler(lambda message: message.text == 'Курс валют', chat_type=types.ChatType.PRIVATE)
async def handle_currency_rates(message: types.Message):
    currency_converter = CurrencyConverter()
    exchange_text, _, _, _ = currency_converter.convert_currency()
    
    await message.reply(exchange_text)