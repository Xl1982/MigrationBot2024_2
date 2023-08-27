
from aiogram import executor, types, dispatcher
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from source.market.filters import IsUser, IsAdmin
from source.config import MARKET_ADMINS
from source.single_chat.admin_commands.start import check_admins
from source.market import handlers
from source import config
from source.data.classes.admin_manager import AdminsManager
from source.bot_init import dp, bot
from source.single_chat.admin_commands.start import info_handler_two
from source.single_chat.start_handler import start_work

text = '''
🛍️ Чтобы перейти в каталог и выбрать приглянувшиеся товары возпользуйтесь командой /menu.
💰 Оплата производится наличными в евро.
❓ Возникли вопросы? Не проблема! Команда /sos поможет связаться с админами, которые постараются как можно быстрее откликнуться.
    '''
text_for_admin = text + ('\nВыбери от чьей роли будешь просматривать маркет. <b>Режим админа</b> позволит его настроить, а <b>режим пользователя</b> - просмотреть и проверить функционал заказа.'
                         ' После выбора режима введи команду /menu (можно просто на неё нажать)')

user_message = 'Пользователь'
admin_message = 'Админ'

@dp.callback_query_handler(lambda c: c.data == 'market')
async def cmd_start_admin(query: types.CallbackQuery):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(user_message, admin_message)
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    await query.answer()
    await query.message.answer(text_for_admin, reply_markup=markup)

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


@dp.callback_query_handler(IsAdmin(), lambda c: c.data == 'market_exit', state='*')
async def market_exit_handler(query: types.CallbackQuery, state: dispatcher.FSMContext = None):
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    await query.answer()
    await info_handler_two(query.message)
    if state:
        await state.finish()

@dp.callback_query_handler(IsUser(), lambda c: c.data == 'market_exit', state='*')
async def market_exit_handler(query: types.CallbackQuery, state: dispatcher.FSMContext = None):
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    await query.answer()
    await start_work(query.message)
    if state:
        await state.finish()
