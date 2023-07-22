
from aiogram import executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from source.single_chat.admin_commands.start import check_admins
from source.market import handlers
from source import config
from source.data.classes.admin_manager import AdminsManager
from source.bot_init import dp


# user_message = 'Пользователь'
# admin_message = 'Админ'

@dp.message_handler(commands='market')
async def cmd_start(message: types.Message):
    # markup = ReplyKeyboardMarkup(resize_keyboard=True)

    # markup.row(user_message, admin_message)

    text = '''Привет! 👋
    🤖 Я бот-магазин по продаже товаров любой категории.
    🛍️ Чтобы перейти в каталог и выбрать приглянувшиеся товары возпользуйтесь командой /menu.
    💰 Пополнить счет можно через Яндекс.кассу, Сбербанк или Qiwi.
    ❓ Возникли вопросы? Не проблема! Команда /sos поможет связаться с админами, которые постараются как можно быстрее откликнуться.
        '''

    # if message.from_user.id in check_admins():
        # await message.answer(text, reply_markup=markup)
    # else:
    await message.answer(text)


# @dp.message_handler(lambda message: message.from_user.id in check_admins(), text=user_message)
# async def user_mode(message: types.Message):
#     user_id = 


# @dp.message_handler(lambda message: message.from_user.id in check_admins(), text=admin_message)
# async def admin_mode(message: types.Message):
#     cid = message.chat.id
#     if cid not in config.ADMINS:
#         config.ADMINS.append(cid)

#     await message.answer('Включен админский режим.', reply_markup=ReplyKeyboardRemove())


