import logging
from dataclasses import dataclass
from typing import List
from aiogram.types import LabeledPrice
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN, TOKEN_PAYMASTER
from filters import AdminFilter
from aiogram import Bot, Dispatcher, executor, types
from filters import AdminFilter

PROVIDER_TOKEN = TOKEN_PAYMASTER

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)



@dataclass()
class Item:
    title: str
    description: str
    start_parameter: str
    currency: str
    prices: List[LabeledPrice]
    provider_data: dict = None
    photo_url: str = None
    photo_size: dict = None
    photo_width: int = None
    photo_height: int = None
    need_name: bool = False
    need_phone_number: bool = False
    need_email: bool = False
    need_shipping_address: bool = False
    send_phone_number_to_provider: bool = False
    is_flexible: bool = False
    provider_token: str = PROVIDER_TOKEN

    def generate_invoices(self):
        return self.__dict__

NoteBook = Item(
    title='NoteBook Lenovo',
    description='insert sample text',
    currency='RUB',
    prices=[
        LabeledPrice(
            label='NoteBook Lenovo',
            amount=30_000_00
        ),
        LabeledPrice(
            label='Доставка',
            amount=500_00
        ),
        LabeledPrice(
            label='Скидка',
            amount=-2_000_00
        )
    ],
    start_parameter='create_invoice_lenovo_3',
    photo_url="https://items.s1.citilink.ru/1595005_v01_b.jpg",
    photo_size=600,
    need_shipping_address=True,
    is_flexible=True
)

#доставка почтой
POST_REGULAR_SHIPPING = types.ShippingOption(
    id='post_reg',
    title='Почтой',
    prices=[
        types.LabeledPrice(
            'Обычная коробка', 0
        ),
        types.LabeledPrice(
            'Почтой', 500_99
        ),
    ]
)


#самовывоз
PICKUP_SHIPPING = types.ShippingOption(
    id='pickup',
    title='Самовыз',
    prices=[
        types.LabeledPrice(
            'Самовывоз из магазина', -1000
        ),
    ]
)


#почта скоростная
POST_FAST_SHIPPING = types.ShippingOption(
    id='post_fast',
    title='Почтой ускоренная',
    prices=[
        types.LabeledPrice(
            'Прочная упаковка', 200_00
        ),
        types.LabeledPrice(
            'Срочной почтой', 1000_00
        ),
    ]
)

# обработчки команды инвойс

@dp.message_handler(commands=('invoces'))
async def show_invoces(message: types.Message):
    await bot.send_invoice(message.from_user.id, **NoteBook.generate_invoices(), payload='12345')


#обработчик доставки
@dp.shipping_query_handler()
async def choose_shipping(query: types.ShippingQuery):
    if query.shipping_address.country_code == 'RU':
        await bot.answer_shipping_query(shipping_query_id=query.id, shipping_options=[
            POST_REGULAR_SHIPPING,
            POST_FAST_SHIPPING,
            PICKUP_SHIPPING
        ], ok=True)
    elif query.shipping_address.country_code == 'US':
        await bot.answer_shipping_query(shipping_query_id=query.id, ok=False, error_message='Доставка недоступна')
    else:
        await bot.answer_shipping_query(shipping_query_id=query.id, shipping_options=[POST_REGULAR_SHIPPING], ok=True)


@dp.pre_checkout_query_handler()
async def process_pre_checkout(query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)
    await bot.send_message(chat_id=query.from_user.id, text='Спасибо за покупке')



if __name__ == "__main__":
   # Запуск бота
   executor.start_polling(dp, skip_updates=True)
