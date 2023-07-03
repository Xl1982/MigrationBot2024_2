from source.config import *
import logging
from aiogram import executor, types, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType


API_TOKEN = BOT_TOKEN
SBER_TOKEN = SBER_TOKEN

logging.basicConfig(level=logging.INFO)

admins = ADMINS

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

class Help(StatesGroup): # класс машины состояния help
   waiting_mesage = State()


# создание клавиатуры

main_keyboard = InlineKeyboardMarkup() # создание объекта для главной клавиатуры

button1 = InlineKeyboardButton('Файл 1', callback_data='file1')
# создание кнопки файл 1, file1

button_cnl = InlineKeyboardButton('Отмена', callback_data='cancel')
# создание кнопки "отмена" - callback data cancel

#add всегда начинает добавление с новой строки и при достижении заданной ширины начинает новую строку
main_keyboard.add(button1) # добавление кнопки файл 1 в главную клавиатуру
main_keyboard.add(button_cnl) # добавление кнопки отмена в главную клавиатуру

keyboard_help = InlineKeyboardMarkup() # объект для клавиатуры помощи
btn_help = InlineKeyboardButton('Помощь', callback_data='help') # создание кнопки помощь где data 'help'
keyboard_help.add(btn_help, button_cnl) # кнопка помощь и кн отмена


@dp.message_handler(commands=['start'])
async def start(message: types.Message): #асинх функц обработки сообщения start
   await message.answer(f'Здравствуйте{message.from_user.username}!') # отправка ответного сообщения
   await message.answer('Для покупки выберите вариант ниже', reply_markup=main_keyboard) # отправка сообщения с главной клавиатурой


@dp.message_handler(commands=['help'])
async def start(message: types.Message):
   await message.answer(f'Выберите необходимое действие', reply_markup=keyboard_help)
   # возвратили сообщение с клавиатурой помощи



@dp.callback_query_handler(text='help')# обработчик келлбек запроса
async def call_help(callback: types.CallbackQuery, state: FSMContext): #асинхн
   await callback.answer() #
   await callback.message.answer('Напишите вашу проблему') #
   await state.set_state(Help.waiting_mesage.state) #

@dp.message_handler(state=Help.waiting_mesage)
async def send_msg(message: types.Message, state: FSMContext):
   text = message.text # получения текста сообщения
   user = message.from_user.username # получение имени пользователя
   await bot.send_message(admins[0], f'Вам сообщзение от {user}\n{text}') # отправка сообщения админу
   await state.finish() # завершение состояния


@dp.callback_query_handler(text='cancel')
async def cancel(callback: types.CallbackQuery): # функция обработки текста cancel
   await bot.delete_message(callback.from_user.id, callback.message.message_id) #удаление сообщения


@dp.callback_query_handler(text='file1')
async def payment(callback: types.CallbackQuery):
   await bot.send_invoice(chat_id=callback.from_user.id, title='Покупка', description='Покупка файла 1',
                          payload='payment', provider_token=SBER_TOKEN, currency='RUB', start_parameter='test_bot',
prices=[{'label': 'Руб', 'amount': 10000}])


@dp.pre_checkout_query_handler()
async def proccess_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
   await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT) # обр с успешной оплатоай
async def process_pay(message: types.Message): # функц обработки сообщения с успешной оплатой
   if message.succesful_payment.invoice_payload == 'payment':# проверка иденд счета
      await bot.send_message(message.from_user.id, 'Вы купили файл')# сообщение польз о покупке
      await message.reply_document(open('file1.txt', "rb")) # отправляем купленный файл



if __name__ == '__main__':
   executor.start_polling(dp, skip_updates=True)
