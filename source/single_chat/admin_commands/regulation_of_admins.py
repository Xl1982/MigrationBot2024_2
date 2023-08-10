import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database.operations.users import User
from source.data.classes.admin_manager import AdminsManager
from source.bot_init import dp, bot
from source.single_chat.admin_commands.start import info_handler


class RegulationOfAdmins(StatesGroup):
    waiting_id_admin_to_add = State()
    waiting_id_admin_to_delete = State()


@dp.callback_query_handler(lambda c: c.data == 'admins')
async def regulation_of_admins(query: types.CallbackQuery):
    await query.answer()

    # Удаляем предыдущее сообщение с помощью метода delete_message
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Удалить администратора', callback_data='delete_admin'))
    keyboard.add(types.InlineKeyboardButton('Добавить администратора', callback_data='add_admin'))
    keyboard.add(types.InlineKeyboardButton('Посмотреть список администраторов', callback_data='check_admins'))
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data='back_admin'))
    await query.message.answer('Выбери что необходимо сделать:', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data == 'back_admin')
async def back_admin(query: types.CallbackQuery):
    # Удаляем предыдущее сообщение с помощью метода delete_message
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    await query.answer()
    await info_handler(query.message)


@dp.callback_query_handler(lambda c: c.data == 'add_admin' or c.data == 'delete_admin')
async def add_admin(query: types.CallbackQuery):
    await query.answer()
    # Удаляем предыдущее сообщение с помощью метода delete_message
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('Назад'))
    await query.message.answer('Введите числовой идентификатор пользователя либо перешлите его сообщение ко мне в чат', reply_markup=keyboard)
    if query.data == 'add_admin':
        await RegulationOfAdmins.waiting_id_admin_to_add.set()
    else:
        await RegulationOfAdmins.waiting_id_admin_to_delete.set()


@dp.message_handler(state=RegulationOfAdmins.waiting_id_admin_to_add)
async def process_admin_info(message: types.Message, state: FSMContext):
    user_id = None
    username = None
    # Определите путь к файлу для администраторов, используя модуль os
    admins_path = os.path.join('source', 'data', 'admins.json')

    # Создайте или работайте с файлом администраторов по указанному пути
    admins_manager = AdminsManager(admins_path)
    # Удаляем предыдущее сообщение с помощью метода delete_message
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if message.text == 'Назад':
        await info_handler(message)
        await state.finish()
        return

    if message.forward_from:
        # Если сообщение было переслано из другого чата, то используем user_id и имя из пересланного сообщения
        user_id = message.forward_from.id
        username = message.forward_from.first_name  

    elif message.text:
        # Если пользователь ввел текст (числовой идентификатор пользователя)
        try:
            user_id = int(message.text)
        except ValueError:
            await message.answer("Неверный формат числового идентификатора пользователя.")
            return
        
        user = User()
        user_data = user.get_user_by_id(user_id)
        if user_data is not None:
            # Используем метод add_admin класса AdminsManager для сохранения данных в файл admins.json
            username = user_data["user_firstname"]
        else:
            await message.answer("Пользователь с таким user_id не найден в базе данных.")
            return


    if user_id is not None and username is not None:
        # Сохраняем данные в файл admins.json с помощью метода add_admin класса AdminsManager
        admins_manager.add_admin(user_id, username)

        await message.answer(f"Пользователь с user_id {user_id} и именем {username} был добавлен в администраторы.")
    else:
        await message.answer("Не удалось получить числовой идентификатор пользователя или имя пользователя.")
        return

    # Завершаем состояние FSM (если используется)
    await state.finish()
    await info_handler(message)


@dp.callback_query_handler(lambda c: c.data == 'check_admins')
async def check_admins(query: types.CallbackQuery):
    # Создаем экземпляр AdminsManager, указывая путь к файлу admins.json
    admins_manager = AdminsManager(r'source\data\admins.json')
    # Удаляем предыдущее сообщение с помощью метода delete_message
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    all_admins = admins_manager.get_all_admins()

    if not all_admins:
        await query.answer("Список администраторов пуст.")
    else:
        message_text = "Список администраторов бота:\n\n"
        for user_id, username in all_admins.items():
            message_text += f"Имя - {username}\nID - {user_id}\n\n"

        await query.answer()
        await query.message.answer(message_text)
    await info_handler(query.message)
    


@dp.message_handler(state=RegulationOfAdmins.waiting_id_admin_to_delete)
async def process_admin_id_to_delete(message: types.Message, state: FSMContext):
    user_id = None
    # Удаляем предыдущее сообщение с помощью метода delete_message
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if message.text == 'Назад':
        await info_handler(message)
        await state.finish()
        return

    if message.forward_from:
        # Если сообщение было переслано из другого чата, то используем user_id из пересланного сообщения
        user_id = message.forward_from.id
    
    elif message.text:
        # Если пользователь ввел текст (числовой идентификатор пользователя)
        try:
            user_id = int(message.text)
        except ValueError:
            await message.answer("Неверный формат числового идентификатора пользователя.")
            return


    if user_id is not None:
        # Создаем экземпляр AdminsManager, указывая путь к файлу admins.json
        admins_manager = AdminsManager(r'source\data\admins.json')

        # Проверяем, существует ли админ с заданным user_id
        if admins_manager.get_admin_by_id(user_id) is not None:
            # Удаляем админа по user_id с помощью метода remove_admin класса AdminsManager
            admins_manager.remove_admin(user_id)
            await message.answer(f"Пользователь с user_id {user_id} был удален из администраторов.")
        else:
            await message.answer("Пользователь с таким user_id не является администратором.")
            return
    else:
        await message.answer("Не удалось получить числовой идентификатор пользователя.")
        return

    # Завершаем состояние FSM (если используется)
    await state.finish()
    await info_handler(message)