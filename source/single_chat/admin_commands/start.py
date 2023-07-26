from aiogram import types

from source.bot_init import dp, bot
from source.config import MAIN_ADMIN
from source.data.classes.admin_manager import AdminsManager

# Создаем функцию для генерации инлайн клавиатуры с кнопками
def make_keyboard(user_id):
    # Создаем объект инлайн клавиатуры
    keyboard = types.InlineKeyboardMarkup()
    # Добавляем кнопки с текстом и коллбэк-данными
    keyboard.add(types.InlineKeyboardButton("Забаненные в личке", callback_data="banned"))
    keyboard.add(types.InlineKeyboardButton("Список заказов такси", callback_data="taxi"))
    keyboard.add(types.InlineKeyboardButton("Список заказов для переводчика", callback_data="translator"))
    keyboard.add(types.InlineKeyboardButton('Отправить сообщение в группы', callback_data='send_messages'))
    # if user_id == MAIN_ADMIN:
    keyboard.add(types.InlineKeyboardButton('Действия с администраторами бота', callback_data='admins'))
    keyboard.add(types.InlineKeyboardButton('Магазин', callback_data='market'))
    keyboard.add(types.InlineKeyboardButton('Настройка сообщений для рассылки', callback_data='messages'))

    # Возвращаем клавиатуру
    return keyboard

def check_admins():
    admins_manager = AdminsManager(r'source\data\admins.json')
    # Получаем список всех user_id администраторов из JSON файла
    all_admin_user_ids = admins_manager.get_all_admin_user_ids()
    return all_admin_user_ids


# Регистрируем обработчик для команды info
@dp.message_handler(lambda message: (message.from_user.id == MAIN_ADMIN or message.from_user.id in check_admins())
                    and message.chat.type == types.ChatType.PRIVATE, commands=["info"])
async def info_handler(message: types.Message):
    
    # Отправляем сообщение с текстом и инлайн клавиатурой
    await message.answer("Выберите действие:", reply_markup=make_keyboard(message.from_user.id))
    