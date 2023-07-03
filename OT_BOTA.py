import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN_GREEN, CHAT_ID_BI
# Установите токен доступа для вашего бота
bot_token = BOT_TOKEN_GREEN
# Установите ID группы или чата, от имени которого нужно отправить сообщение
group_id = CHAT_ID_BI

# Инициализация бота и диспетчера
bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Включение логирования
logging.basicConfig(level=logging.INFO)




# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Отправляем сообщение от имени группы
    await bot.send_message(chat_id=group_id, text='Привет, это сообщение от имени группы!')

# Запуск бота
if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)