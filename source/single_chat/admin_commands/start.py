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
    
    info_text = (
        "<b>У тебя есть перечень кнопок, который отвечает за различные действия.</b> Что делает та или иная кнопка, отражено в её названии. Помимо того, бот умеет функционировать в группах.\n"
        "/ban - необходимо использовать ответом на сообщение. <i>Банит участника.</i>\n"
        "/unban - либо ответ на сообщение, либо ID пользователя аргументом. <i>Позволяет участнику вернуться в чат.</i>\n"
        "/mute - используется ответом на сообщение участника. <i>Запрещает отправлять сообщения в течение 24 часов.</i>\n"
        "/unmute - механизм аналогичен команде разбана. <i>Дает досрочное освобождение от запрета отправки сообщений.</i>\n\n"
        "<b>Бот приветствует участников в чате, отправляет некоторые сообщения в определенное время (погода, курс валюты, объявление о покупке валюты),</b>"
        " запрещает пересылать сообщения от куда-либо в чат.\n\n"
        "<i>Текстовые рассылки можно сделать самому, для этого надо нажать на кнопку \"Настройка сообщений для рассылки\".</i>"
        "\n\nФункционалом администратора (этой командой) могут пользоваться и другие люди, для этого их нужно добавить через кнопку \"Действия с администраторами бота\"."
        "\n\nЧерез кнопку \"Отправить сообщение в группы\" происходит отправка сообщений в добавленные чаты. Чат добавляется в список рассылочных чатов"
        " через команду <code>/add_chat</code> внутри него. То есть нам нужно зайти в чат, который мы хотим добавить в список чатов для рассылки сообщений,"
        " туда добавить бота, дать ему права админа и использовать команду <code>/add_chat</code>. Для удаления - <code>/remove_chat</code>."
    )
    await message.answer(info_text)
    # Отправляем сообщение с текстом и инлайн клавиатурой
    await message.answer("Выберите действие:", reply_markup=make_keyboard(message.from_user.id))