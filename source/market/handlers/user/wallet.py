from source.bot_init import dp
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from source.market.filters import IsUser
from .menu import balance


@dp.message_handler(IsUser(), text=balance)
async def process_balance(message: Message, state: FSMContext):
    await message.answer('В разработке.')
    # await message.answer('Ваш кошелек пуст! Чтобы его пополнить нужно...')
