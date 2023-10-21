import aiogram
import asyncio


async def del_message_in_time(message: aiogram.types.Message):
    await asyncio.sleep(24600)
    await    message.delete()
