import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from source.bot_init import dp, bot
from source.config import MAIN_ADMIN
from source.data.classes.admin_manager import AdminsManager
from source.data.classes.add_chat import ChatManager
from source.market.filters import IsAdmin

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


class ChatEditStates(StatesGroup):
    choose_chat = State()
    get_welcome_text = State()
    wait_ru_city = State()
    wait_en_city = State()



# Создаем функцию для генерации инлайн клавиатуры с кнопками
def make_keyboard():
    # Создаем объект инлайн клавиатуры
    keyboard = types.InlineKeyboardMarkup()
    # Добавляем кнопки с текстом и коллбэк-данными
    keyboard.add(types.InlineKeyboardButton("Забаненные в личке", callback_data="banned"))
    keyboard.add(types.InlineKeyboardButton("Список заказов такси", callback_data="taxi"))
    keyboard.add(types.InlineKeyboardButton("Список заказов для переводчика", callback_data="translator"))
    keyboard.add(types.InlineKeyboardButton('Отправить сообщение в группы', callback_data='send_messages'))
    keyboard.add(types.InlineKeyboardButton('Действия с администраторами бота', callback_data='admins'))
    keyboard.add(types.InlineKeyboardButton('Спам-фильтр', callback_data='spam_filter'))
    keyboard.add(types.InlineKeyboardButton('Магазин', callback_data='market'))
    keyboard.add(types.InlineKeyboardButton('Выход', callback_data='exit_settings_state'))

    # Возвращаем клавиатуру
    return keyboard

def check_admins():
    path = os.path.join('source', 'data', 'admins.json')
    admins_manager = AdminsManager(path)
    # Получаем список всех user_id администраторов из JSON файла
    all_admin_user_ids = admins_manager.get_all_admin_user_ids()
    return all_admin_user_ids


@dp.message_handler(lambda message: (message.from_user.id == MAIN_ADMIN or message.from_user.id in check_admins())
                    and message.chat.type == types.ChatType.PRIVATE, commands=["chats"])
async def start_chats_settings(message: types.Message):
    # Отправляем сообщение с текстом и инлайн клавиатурой
    path = os.path.join('source', 'data', 'chats.json')
    chat_manager = ChatManager(path)

    chat_ids = chat_manager.get_all_chat_ids()
    keyboard = types.InlineKeyboardMarkup(row_width=1)  # Один чат на строку

    if chat_ids:
        for chat_id in chat_ids:
            chat_data = chat_manager.get_chat_data(chat_id)
            chat_title = chat_data.get('title', 'Нет названия')
            keyboard.add(types.InlineKeyboardButton(chat_title, callback_data=str(chat_id))) 
        keyboard.add(types.InlineKeyboardButton('Выход', callback_data='exit_settings_state'))
        await message.answer('Выберите чат для настройки:', reply_markup=keyboard)
        await ChatEditStates.choose_chat.set()
    else:
        await message.answer('У вас нет чатов для настройки. Введите /add_chat в чате, где есть бот.')


@dp.callback_query_handler(lambda c: c.data == 'exit_settings_state', state='*')
async def exit_settings_chat(query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    await query.answer()
    await query.message.answer('Вы вышли из настроек чата. Для действий введите /chats или /info')
    await state.finish()


# Регистрируем обработчик для команды info
@dp.message_handler(lambda message: (message.from_user.id == MAIN_ADMIN or message.from_user.id in check_admins())
                    and message.chat.type == types.ChatType.PRIVATE, commands=["info"])
async def info_handler(message: types.Message):
    await message.answer(info_text)
    await message.answer('Выберите действие:', reply_markup=make_keyboard())

@dp.message_handler(IsAdmin(), lambda message: message.text == 'Выход' and message.chat.type == types.ChatType.PRIVATE, state='*')
async def info_handler_two(message: types.Message, state: FSMContext = None):
    if state:
        await state.finish()
    await message.answer('Выберите действие: ', reply_markup=make_keyboard())