from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from source.single_chat.start_handler import start_work
from source.config import MAIN_ADMIN
from source.bot_init import dp, bot

from database.operations.users import User

ADMIN_ID = MAIN_ADMIN


'''
По-хорошему в личку могут спамить много людей и будет всякий бред
Администратор обязан себя ограничивать от такого в любом случае, иначе - потеря времени на просмотр
бесполезной информации

Исходя из этого очевидным становится необходимость реализации блокировки пользователей по их user_id
То есть у админа может быть команда типа @user id бан после чего бот заносит пользователя в чёрный список
и пользователь этот не имеет возможности более связаться с админом через бота

Однако необходимо оставить такой простор для базы данных, где мы и будем отмечать блокировку пользователя.
Сейчас базы данных нет, потому будет функция которая говорит что пользователя мы забанили, но действий в базу данных не внесли.
Это уже будет потом реализовано

P.S. - Сделано в связи с подключением Postgres 
'''


# обработчик текста 'Написать админу'
@dp.message_handler(lambda message: message.text == "Написать админу" and message.chat.type == types.ChatType.PRIVATE)
async def write_admin(message: types.Message):
    user = User()
    # проверяем, не забанен ли пользователь
    if not user.check_ban_status(user_id=message.from_user.id):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Назад'))
        await message.answer("Пожалуйста, напиши текст сообщения для админа.", reply_markup=keyboard)
        # устанавливаем состояние для пользователя
        await dp.current_state(user=message.from_user.id).set_state("write_message")
    else:
        # если пользователь забанен, то не даем ему писать админу
        await message.answer("Извини, но ты не можешь связаться с админом. Ты был забанен за нарушение правил.")

# обработчик состояния 'write_message'
@dp.message_handler(state="write_message")
async def send_message(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        await state.finish()
        await start_work(message)
        return
    
    # получаем текст сообщения от пользователя
    user_message = message.text
    # получаем username и id пользователя
    user_username = message.from_user.username
    user_id = message.from_user.id
    # пересылаем сообщение админу с username и id пользователя
    await bot.send_message(ADMIN_ID, f"Сообщение от {message.from_user.full_name} (@{user_username}, {user_id}):\n<<{user_message}>>. "
                           f'\n\nДля отправки ответного сообщения введи @{user_id} <ответ>')
    # уведомляем пользователя о передаче сообщения
    await message.answer("Сообщение успешно отправлено админу. Пожалуйста, подожди, пока он свяжется с тобой.")
    # сбрасываем состояние для пользователя
    await dp.current_state(user=message.from_user.id).reset_state()

# обработчик сообщений от админа
@dp.message_handler(lambda message: message.from_user.id == ADMIN_ID and message.text.startswith('@') and
                    message.chat.type == types.ChatType.PRIVATE)
async def reply_user(message: types.Message):
    # получаем текст сообщения от админа
    admin_message = message.text
    # проверяем, что сообщение содержит id пользователя в начале
    try:
        if admin_message.startswith("@"):
            # разбиваем сообщение на id пользователя и текст ответа или команду бана
            user_id, reply_text_or_ban = admin_message.split(" ", 1)
            # удаляем символ @ из id пользователя и преобразуем его в число
            user_id = int(user_id[1:])
            # проверяем, что команда бана это "бан"
            if reply_text_or_ban == "бан":
                # баним пользователя по его id (пока без базы данных)
                user = User()
                user.toggle_ban_status(user_id)
                # уведомляем админа об успешной блокировке пользователя
                await message.answer(f"Пользователь с id {user_id} успешно забанен.")
            else:
                # если команда бана не "бан", то считаем это текстом ответа и пересылаем его пользователю по его id
                await bot.send_message(user_id, f"Сообщение от админа:\n{reply_text_or_ban}")
                # уведомляем админа об успешной отправке ответа
                await message.answer(f"Ответ успешно отправлен пользователю с id {user_id}.")
        else:
            # если сообщение не содержит id пользователя в начале, то игнорируем его
            await message.answer("Неверный формат сообщения. Для отправки ответа пользователю введите его id с символом @ в начале, затем пробел и текст ответа. Для блокировки пользователя введите его id с символом @ в начале, затем пробел и команду 'бан'.")
    except Exception as e:
        await bot.send_message(ADMIN_ID, "Проблема с отправкой сообщения. Проверь корректность своего ответа для его отправки. "
                               "Должно быть @<user_id> <text>")
        print(f'Ошибка при отправке ответа админа пользователю - {e}')

