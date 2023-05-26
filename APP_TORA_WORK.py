import asyncio
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
#from config import BOT_TOKEN, CHAT_ID, api_key, api_exchange

from config import BOT_TOKEN, CHAT_ID_TORA, api_key, api_exchange
CHAT_ID = CHAT_ID_TORA
from pogodaTor import WeatherAPI, weather_text
from xchange010 import CurrencyConverter, exchange_text

now0 = datetime.datetime.now()
print(now0)



bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

async def send_weather_message():
    await bot.send_message(CHAT_ID, weather_text)

async def send_exchange_message():
    await bot.send_message(CHAT_ID, exchange_text)

@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def greet_new_member(message: types.Message):
    new_members = message.new_chat_members
    for member in new_members:
        greeting_message = await message.reply(f"Привет, {member.first_name}! Добро пожаловать в чат 📢Торревьеха!\n"
                                               f"\n"
                                               f"Поприветствуем нового пользователя!\n"
                                               f"\n"
                                               f"📍Мы собрали здесь информацию о самых актуальных объявлениях, связанных с жизнью в прекрасном городе Торревьеха.\n"
                                               f"\n"
                                               f"Если вы ищете аренду жилья🏡, продажу недвижимости, работу, услуги🛠 или просто хотите быть в курсе новостей, этот канал - идеальное место для вас.\n")

        await asyncio.sleep(120)  # Задержка в 5 минут (300 секунд)
        print(f"{member.first_name}")
        await greeting_message.delete()


async def send_messages_periodically():
    while True:
        now = datetime.datetime.now()
        if now.hour == 13 and now.minute == 15:
            await send_weather_message()
            print("Отравленно в группу погода")

        elif now.hour == 13 and now.minute == 36:
            await send_exchange_message()
            print("Отравленно в группу курс валют")
        await asyncio.sleep(60)  # Проверка каждую минуту


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_messages_periodically())
    executor.start_polling(dp, loop=loop)
