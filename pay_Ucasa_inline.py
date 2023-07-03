import logging
from aiogram import executor, Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType

from config import BOT_TOKEN, UKASSA_TOKEN, ADMINS

logging.basicConfig(level=logging.INFO)

subscribers = []
admins = ADMINS

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Создание клавиатуры
keyboard = InlineKeyboardMarkup()
btn_payment = InlineKeyboardButton('Оплатить', callback_data='payment')
btn_cancel = InlineKeyboardButton('Отмена', callback_data='cancel')
keyboard.add(btn_payment, btn_cancel)

# Создание клавиатуры для проверки подписки
keyboard_check = InlineKeyboardMarkup()
btn_check = InlineKeyboardButton('Проверить подписку', callback_data='check')
keyboard_check.add(btn_check)


# Обработчик на нажатие кнопки reply
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def reply_handler(message: types.Message):
    id = str(message.from_user.id)
    if id in subscribers or id in admins:
        username = message.from_user.username
        await message.reply(f"Добро пожаловать, {username}!", reply_markup=keyboard)
    else:
        await message.reply("Для начала работы подпишитесь", reply_markup=keyboard)


# Обработчик команды /payment
@dp.message_handler(commands=['payment'])
async def payment(message: types.Message):
    await bot.send_invoice(chat_id=message.chat.id, title='Подписка', description='Подписка на бота',
                           payload='payment', provider_token=UKASSA_TOKEN, currency='RUB', start_parameter='test_bot',
                           prices=[{'label': 'Руб', 'amount': 10000}])  # Отправляем счет для оплаты


# Обрабочтик команды /help
@dp.message_handler(commands=['help'])
async def help_message(message: types.Message):
    await message.reply('Вы находитесь в информационном боте\n'
                        'Если вы оформили подписку, но она не активна\n'
                        'Напишите админу @логин\n', reply_markup=keyboard_check)


# Обработчик нажатия на кнопку оплатить
@dp.callback_query_handler(text='payment')
async def payment_callback(callback: types.CallbackQuery):
    await callback.answer()
    await bot.send_invoice(chat_id=callback.from_user.id, title='Подписка', description='Подписка на бота',
                           payload='payment', provider_token=UKASSA_TOKEN, currency='RUB', start_parameter='test_bot',
                           prices=[{'label': 'Руб', 'amount': 10000}])  # Отправляем счет для оплаты


# Обработчик проверки перед оплатой
@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# Обработчик успешной оплаты
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_pay(message: types.Message):
    if message.successful_payment.invoice_payload == 'payment':
        await bot.send_message(message.from_user.id, 'Вы подписались')
        subscribers.append(str(message.from_user.id))


# Обработчик нажатия проверить подписку
@dp.callback_query_handler(text='check')
async def check_sub(callback: types.CallbackQuery):
    await callback.answer()
    id = str(callback.from_user.id)
    if id in admins:
        await callback.message.reply('Вы администратор')
    elif id in subscribers:
        await callback.message.reply('Подписка активна')
    else:
        await callback.message.reply('Подписка не активна', reply_markup=keyboard)


# Обработчик кнопки отмена
@dp.callback_query_handler(text='cancel')
async def cancel_callback(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.reply("Вы отказались")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
