from aiogram import types

from source.bot_init import dp, bot
from source.config import MAIN_ADMIN


# Создаем функцию для генерации инлайн клавиатуры с кнопками
def make_keyboard():
    # Создаем объект инлайн клавиатуры
    keyboard = types.InlineKeyboardMarkup()
    # Добавляем кнопки с текстом и коллбэк-данными
    keyboard.add(types.InlineKeyboardButton("Забаненные в личке", callback_data="banned"))
    keyboard.add(types.InlineKeyboardButton("Список заказов такси", callback_data="taxi"))
    keyboard.add(types.InlineKeyboardButton("Список заказов для переводчика", callback_data="translator"))
    # Возвращаем клавиатуру
    return keyboard

# Регистрируем обработчик для команды info
@dp.message_handler(lambda message: message.from_user.id == MAIN_ADMIN, commands=["info"])
async def info_handler(message: types.Message):
    # Отправляем сообщение с текстом и инлайн клавиатурой
    await message.answer("Выберите действие:", reply_markup=make_keyboard())
    