from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ChatType
from source.bot_init import dp
from source.market.filters import IsAdmin, IsUser

catalog = '🛍️ Каталог'
balance = '💰 Баланс'
cart = '🛒 Корзина'
delivery_status = '🚚 Статус заказа'

settings = '⚙️ Настройка каталога'
orders = '🚚 Заказы'
questions = '❓ Вопросы'

@dp.callback_query_handler(lambda c: c.data == 'market')
async def admin_menu(query: CallbackQuery):
    markup = ReplyKeyboardMarkup(selective=True)
    markup.add(settings)
    markup.add(questions, orders)

    await query.message.answer('Меню', reply_markup=markup)

@dp.message_handler(lambda message: message.chat.type == ChatType.PRIVATE, text='Магазин')
async def user_menu(message: Message):
    markup = ReplyKeyboardMarkup(selective=True)
    markup.add(catalog)
    markup.add(balance, cart)
    markup.add(delivery_status)

    await message.answer('Меню', reply_markup=markup)