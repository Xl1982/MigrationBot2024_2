from aiogram.types import Message
from source.bot_init import dp, db
from .menu import delivery_status
from source.market.filters import IsUser


@dp.message_handler(IsUser(), text=delivery_status)
async def process_delivery_status(message: Message):
    query = '''
        SELECT o.order_id, o.usr_name, o.usr_address, o.products, o.sending
        FROM orders o
        WHERE o.cid = %s
    '''

    user_orders_data = db.fetchall(query, (message.chat.id,))

    if len(user_orders_data) == 0:
        await message.answer('У вас нет активных заказов.')
    else:
        await delivery_status_answer(message, user_orders_data)


async def delivery_status_answer(message, user_orders_data):
    res = ''

    for order in user_orders_data:
        order_id = order[0]
        usr_name = order[1]
        usr_address = order[2]
        products = order[3]
        sending = order[4]

        status = "лежит на складе." if not sending else "уже в пути!"  # Define the status message based on sending flag

        products_info = []

        if products:
            product_entries = products.split(',')
            for entry in product_entries:
                entry_split = entry.split('=')
                idx = entry_split[0]
                quantity = entry_split[1]
                product_info = db.fetchone('SELECT title, tag FROM products WHERE idx = %s', (idx,))
                if product_info:
                    product_title = product_info[0]
                    product_tag = product_info[1]
                    products_info.append(f'{product_title} ({product_tag}), Количество: {quantity}')
                else:
                    products_info.append('Товар не найден')

        products_info_str = '\n'.join(products_info)

        res += (
            f'Заказ <b>№{order_id}</b>\n'
            f'Имя: {usr_name}\n'
            f'Адрес: {usr_address}\n'
            f'Товары:\n{products_info_str}\n'
            f'Статус: {status}\n\n'
        )

    await message.answer(res, parse_mode='HTML')