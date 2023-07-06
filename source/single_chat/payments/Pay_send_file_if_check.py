import logging
from aiogram import executor, types, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType
from source.config import BOT_TOKEN, SBER_TOKEN, UKASSA_TOKEN, ADMINS

API_TOKEN = "1979946920:AAEu9SuXey8_Zh9yaBeDij8yAF8LdlrZQ3E"
SBER_TOKEN = "381764678:TEST:58192"
logging.basicConfig(level=logging.INFO)


admins = ADMINS
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

# определение состояний используемых в боте
class Help(StatesGroup):
    waiting_message = State()


# создание основной клавиатуры
main_keyboard = InlineKeyboardMarkup()
button1 = InlineKeyboardButton('file1', callback_data='file1') # кнопка для выбора файла
button_cnl = InlineKeyboardButton("Отмена", callback_data='cancel')
main_keyboard.add(button1)
main_keyboard.add(button_cnl)

# создание клавиатуры для помощи
keyboard_help = InlineKeyboardMarkup()
btn_help = InlineKeyboardButton('Помощь', callback_data='help') # кнопка помощи
keyboard_help.add(btn_help, button_cnl)

# команд старт
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    # отправка приветственного сообщения основной клавиатуры
    await message.answer(f'Здравствуйте {message.from_user.username}!')
    await message.answer('Для покупки выберите необходимый вариант ниже',
                         reply_markup=main_keyboard)


# обработчик команды /help
@dp.message_handler(commands=['help'])
async def start(message: types.Message):
    await message.answer(f"выберите необходимое действие",
                         reply_markup=keyboard_help)

# обработчик нажатия на кнопку "Помощь"
@dp.callback_query_handler(text='help')
async def cal_help(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    # запрос на указание проблемы
    await callback.message.answer('Напиште вашу проблему')
    # установка состояния ожидания сообщения
    await state.set_state(Help.waiting_message.state)

# обработчик состояния ожидания сообщения на Хелп
@dp.message_handler(state=Help.waiting_message)
async def send_msg(message: types.Message, state: FSMContext):
    text = message.text # текст сообщения пользователя
    user = message.from_user.username # имя пользователя
    await bot.send_message(admins[0], f'Вам сообщение от {user}\n'
                           f'{text}')
    await state.finish()


# обработчик нажатия на кнопку отмена
@dp.callback_query_handler(text='cancel')
async def cancel(callback: types.CallbackQuery):
    # удаление сообщения
    await bot.delete_message(callback.from_user.id, callback.message.message_id)



# обработчик нажатия на кнопку файл 1
@dp.callback_query_handler(text='file1')
async def payment(callback: types.CallbackQuery):
    await bot.send_invoice(chat_id=callback.from_user.id, title='Покупка', description='Покупка файла 1',
                           payload='payment', provider_token=SBER_TOKEN, currency='RUB', start_parameter='test_bot',
                           prices=[{'label': 'Руб', "amount": 10000}])



# обработчик запроса на оплату
@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    # подтверждение оплаты
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)





# обработчик успешной оплаты
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_pay(message: types.Message):
    if message.successful_payment.invoice_payload == 'payment':
        # подтверждение оплаты и отправка файла
        await bot.send_message(message.from_user.id, "вы купили файл")
        await message.reply_document(open("01.html", 'rb'))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)