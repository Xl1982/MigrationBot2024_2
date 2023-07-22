from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from .config import MAIN_TOKEN_BOT
from source.market.db import DatabaseManager


TOKEN = MAIN_TOKEN_BOT

db = DatabaseManager('telegram_database', 'postgres', 'postgres', 'localhost', '5432')
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)