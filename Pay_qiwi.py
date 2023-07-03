import logging
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN


bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

p2p_url = "https://oplata.qiwi.com/form?invoiceUid=3de6d131-241e-4b75-8e69-68dfc1b85280"
class PayKb(types.InlineKeyboardMarkup):
    def __init__(self, row_width=3, inline_keyboard=None, **kwargs):
        # вызываем род класс
        super().__init__(row_width, inline_keyboard, **kwargs)
        self.add(types.InlineKeyboardButton("Оплатить", p2p_url))


@dp.message_handler(commands=['pay'])
async def send_qiwi_invoice(message: types.Message):
    await message.answer_photo("https://items.s1.citilink.ru/1595005_v01_b.jpg", "Подписка на месяц услуг", reply_markup=PayKb())


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

