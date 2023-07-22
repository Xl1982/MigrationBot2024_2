
from aiogram import executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from source.config import MARKET_ADMINS
from source.single_chat.admin_commands.start import check_admins
from source.market import handlers
from source import config
from source.data.classes.admin_manager import AdminsManager
from source.bot_init import dp

text = '''Привет! 👋
    🤖 Я бот-магазин по продаже товаров любой категории.
    🛍️ Чтобы перейти в каталог и выбрать приглянувшиеся товары возпользуйтесь командой /menu.
    💰 Пополнить счет можно через Яндекс.кассу, Сбербанк или Qiwi.
    ❓ Возникли вопросы? Не проблема! Команда /sos поможет связаться с админами, которые постараются как можно быстрее откликнуться.
        '''
user_message = 'Пользователь'
admin_message = 'Админ'

@dp.callback_query_handler(lambda c: c.data == 'market')
async def cmd_start_admin(query: types.CallbackQuery):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(user_message, admin_message)
    await query.message.answer(text, reply_markup=markup)

@dp.message_handler(lambda message: message.chat.type == types.ChatType.PRIVATE, text='Магазин')
async def cmd_start(message: types.Message):

    await message.answer(text)
    

@dp.message_handler(text=user_message)
async def user_mode(message: types.Message):
    user_id = message.from_user.id
    if user_id in MARKET_ADMINS:
        MARKET_ADMINS.remove(user_id)
    await message.answer('Включен пользовательский режим.', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(text=admin_message)
async def admin_mode(message: types.Message):
    cid = message.chat.id
    if cid not in MARKET_ADMINS:
        MARKET_ADMINS.append(cid)

    await message.answer('Включен админский режим.', reply_markup=ReplyKeyboardRemove())


