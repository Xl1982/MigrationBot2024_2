import logging

from aiogram import executor, types, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType

from config import *
logging.basicConfig(level=logging.INFO)

admins = ADMINS
API_TOKEN = BOT_TOKEN
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

storage = MemoryStorage()
SBER_TOKEN = SBER_TEST_API


class Help(StatesGroup):
    waiting_message = State()





main_kb = InlineKeyboardMarkup()
button1 = InlineKeyboardButton('Файл 1', callback_data='file1')
button_cancel = InlineKeyboardButton('Отмена', callback_data='cancel')
main_kb.add(button1).add(button_cancel)

kb_help = InlineKeyboardMarkup()
button_help = InlineKeyboardButton('помощь', callback_data='help')
kb_help.add(button_help, button_cancel)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer(f'Здравствуйте{message.from_user.username}!')
    await message.answer('Для покупки выберите вариант ниже', reply_markup=main_kb)


@dp.message_handler(commands='help')
async def start(message: types.Message):
    await message.answer(f'Выберите необходимое действие', reply_markup=kb_help)


@dp.callback_query_handler(text='help')
async def help_message(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer('Опишите свою проблему, и мы постараемся вам помочь')
    await state.set_state(Help.waiting_message.state)





@dp.message_handler(state=Help.waiting_message)
async def send_message(message: types.Message, state: FSMContext):
    text = message.text
    user = message.from_user.username
    await bot.send_message(admins[0], f'Вам сообщение от {user}\n{text}')
    await state.finish()


@dp.callback_query_handler(text='cancel')
async def cancel(callback: types.CallbackQuery):
    await bot.delete_message(callback.from_user.id, callback.message.message_id)


@dp.callback_query_handler(text='file1')
async def payment(callback: types.CallbackQuery):
    await bot.send_invoice(chat_id=callback.from_user.id, title='Покупка', description='Покупка файла 1',
                           payload='payment', provider_token=SBER_TOKEN, currency='RUB', start_parameter='test_bot',
                           prices=[{'label': 'Руб', 'amount': 10000}])


@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_pay(message: types.Message):
    if message.successful_payment.invoice_payload == 'payment':
        await bot.send_message(message.from_user.id, 'Вы купили файл')
        await message.reply_document(open('file1.txt', 'rb'))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)