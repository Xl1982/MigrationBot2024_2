import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType
from config import BOT_TOKEN, UKASSA_TOKEN, ADMINS

logging.basicConfig(level=logging.INFO)

subscribers = []
admins = ADMINS

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Создание клавиатуры
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
pay_button = KeyboardButton('Оплатить')
#cancel_button = KeyboardButton('Отмена')

#keyboard.add(pay_button, cancel_button)
keyboard.add(pay_button)
# Создание клавиатуры для проверки подписки
keyboard_check = ReplyKeyboardMarkup(resize_keyboard=True)
btn_check = KeyboardButton('Проверить подписку')
keyboard_check.add(btn_check)


@dp.message_handler()
async def process_start_command(message: types.Message):
    if message.text == 'Оплатить':
        await bot.send_invoice(chat_id=message.chat.id, title='Подписка', description='Подписка на бота',
                               payload='payment', provider_token=UKASSA_TOKEN, currency='RUB',
                               start_parameter='test_bot',
                               prices=[{'label': 'Руб', 'amount': 10000}])  # Отправляем счет для оплаты
    elif message.text == 'Отмена':
        await message.reply("Вы отказались")
    elif message.text == 'Проверить подписку':
        id = str(message.from_user.id)
        if id in admins:
            await message.reply('Вы администратор')
        elif id in subscribers:
            await message.reply('Подписка активна')
        else:
            await message.reply('Подписка не активна', reply_markup=keyboard)
    else:
        id = str(message.from_user.id)
        if id in subscribers or id in admins:
            username = message.from_user.username
            await message.reply(f"Добро пожаловать, {username}!", reply_markup=keyboard)
        else:
            await message.reply("Для начала работы подпишитесь", reply_markup=keyboard)


@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_pay(message: types.Message):
    if message.successful_payment.invoice_payload == 'payment':
        await bot.send_message(message.from_user.id, 'Вы подписались')
        subscribers.append(str(message.from_user.id))


if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
