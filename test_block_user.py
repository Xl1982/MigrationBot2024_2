import sqlite3
import logging
from aiogram import Bot, Dispatcher, types
from filters import IsAdmin
from aiogram.dispatcher.filters import Command
from datetime import timedelta
from config import BOT_TOKEN_GREEN

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем бота и диспетчера
bot = Bot(token=BOT_TOKEN_GREEN)
dp = Dispatcher(bot)

# Создаем соединение с базой данных SQLite
conn = sqlite3.connect('bot.db')
cursor = conn.cursor()

# Создаем таблицу для состояний блокировки
cursor.execute('''
    CREATE TABLE IF NOT EXISTS blocked_users (
        chat_id INTEGER,
        user_id INTEGER,
        expires INTEGER,
        PRIMARY KEY (chat_id, user_id)
    )
''')
conn.commit()

# Хендлер для административной команды блокировки
@dp.message_handler(Command('block_user'), IsAdmin())
async def block_user(message: types.Message):
    # Получаем айди пользователя, которого необходимо заблокировать
    user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id

    # Получаем объект пользователя
    member = await bot.get_chat_member(chat_id, user_id)

    # Вычисляем время истечения состояния блокировки (24 часа)
    expires = int((message.date + timedelta(days=1)).timestamp())

    # Сохраняем состояние блокировки пользователя в базе данных
    cursor.execute('INSERT OR REPLACE INTO blocked_users (chat_id, user_id, expires) VALUES (?, ?, ?)', (chat_id, user_id, expires))
    conn.commit()

    # Логирование блокировки пользователя
    logger.info(f"Пользователь {member.user.username} заблокирован на 24 часа.")

    await message.reply(f"Пользователь {member.user.username} заблокирован на 24 часа.")

# Хендлер для административной команды разблокировки
@dp.message_handler(Command('unblock_user'), IsAdmin())
async def unblock_user(message: types.Message):
    # Получаем айди пользователя, которого необходимо разблокировать
    user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id

    # Получаем объект пользователя
    member = await bot.get_chat_member(chat_id, user_id)

    # Удаляем состояние блокировки пользователя из базы данных
    cursor.execute('DELETE FROM blocked_users WHERE chat_id = ? AND user_id = ?', (chat_id, user_id))
    conn.commit()

    # Логирование разблокировки пользователя
    logger.info(f"Пользователь {member.user.username} разблокирован.")

    await message.reply(f"Пользователь {member.user.username} разблокирован.")

# Хендлер для всех входящих сообщений
@dp.message_handler()
async def process_message(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Получаем объект пользователя
    member = await bot.get_chat_member(chat_id, user_id)

    # Проверяем, заблокирован ли пользователь
    cursor.execute('SELECT expires FROM blocked_users WHERE chat_id = ? AND user_id = ?', (chat_id, user_id))
    result = cursor.fetchone()

    if result and result[0] >= message.date.timestamp():
        # Если пользователь заблокирован, удаляем его сообщение
        await message.delete()

        # Логирование удаления сообщения
        logger.info(f"Удалено сообщение от пользователя {member.user.username}.")

        return

    # Логирование обработки сообщения
    logger.info(f"Обработка сообщения от пользователя {member.user.username}.")

    # Обработка сообщения
    #await message.reply("Ваше сообщение будет обработано.")

# Запуск бота
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
