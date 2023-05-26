import logging
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN


bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

p2p_url = "https://oplata.qiwi.com/form?invoiceUid=a00795a3-74fe-44c3-a514-93b59e608251&successUrl=https%3A%2F%2Ftelegra.ph%2FSpasibo-za-oplatu-05-21"

class PayKb(types.InlineKeyboardMarkup):
    def __init__(self, row_width=3, inline_keyboard=None, **kwargs):
        super().__init__(row_width, inline_keyboard, **kwargs)
        self.add(types.InlineKeyboardButton("Оплатить", p2p_url))


@dp.message_handler(commands=['start'])
async def send_qiwi_invoice(message: types.Message):
    await message.answer_photo("https://items.s1.citilink.ru/1595005_v01_b.jpg", "Ноутбук Lenovo IP Gaming 3",
                               reply_markup=PayKb())


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)