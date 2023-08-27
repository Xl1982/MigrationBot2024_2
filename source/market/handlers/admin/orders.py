from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from source.bot_init import dp, db, bot
from source.market.handlers.user.menu import orders
from source.market.filters import IsAdmin


# Много нулл значений. Нужно переписать обращение к базе данных. Вот как выглядит сейчас:
# Заказ №1
# Имя: марк
# Адрес: шосс
# Товары:
#  - None (None), Количество: None, Цена: None


@dp.message_handler(IsAdmin(), text=orders)
async def process_orders(message: Message):
    query = '''
        SELECT o.order_id, o.usr_name, o.usr_address, o.products, o.sending
        FROM orders o
        WHERE o.sending = FALSE
    '''

    unsent_orders_data = db.fetchall(query)

    if len(unsent_orders_data) == 0:
        await message.answer('Нет непосланных заказов.')
    else:
        for order in unsent_orders_data:
            order_id = order[0]
            usr_name = order[1]
            usr_address = order[2]
            products = order[3]
            sending = order[4]

            products_info = []

            if products:
                product_entries = products.split(',')
                for entry in product_entries:
                    parts = entry.split('=')
                    if len(parts) == 2:
                        idx, quantity = parts
                        product_info = db.fetchone('SELECT title, tag, price FROM products WHERE idx = %s', (idx,))
                        if product_info:
                            product_title = product_info[0]
                            product_tag = product_info[1]
                            product_price = product_info[2]
                            products_info.append(f'{product_title} ({product_tag}), Количество: {quantity}, Цена: {product_price}')
                        else:
                            products_info.append('Товар не найден')
                    else:
                        products_info.append('Некорректная запись товара')
            
            products_info_str = '\n'.join(products_info)

            status = "лежит на складе." if not sending else "уже в пути!"  # Define the status message based on sending flag

            res = (
                f'Заказ №{order_id}\n'
                f'Имя: {usr_name}\n'
                f'Адрес: {usr_address}\n'
                f'Товары:\n{products_info_str}\n'
                f'Статус: {status}\n\n'
            )

            markup = InlineKeyboardMarkup()

            button = InlineKeyboardButton(
                text='Отправить заказ',
                callback_data=f'send_order:{order_id}'
            )
            markup.add(button)

            await message.answer(res, parse_mode='HTML', reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data.startswith('send_order'))
async def send_order_callback(callback_query: CallbackQuery):
    order_id = callback_query.data.split(':')[1]  # Extract order ID from the callback data
    
    # Get the order details based on order_id
    order_details = db.fetchone('SELECT usr_name, usr_address, products FROM orders WHERE order_id = %s', (order_id,))
    if order_details:
        usr_name = order_details[0]
        usr_address = order_details[1]
        products = order_details[2]

        # Parse the products information
        products_info = []
        product_entries = products.split(',') if products else []
        for entry in product_entries:
            idx, quantity = entry.split('=')
            product_info = db.fetchone('SELECT title, tag FROM products WHERE idx = %s', (idx,))
            if product_info:
                product_title = product_info[0]
                product_tag = product_info[1]
                products_info.append(f'{product_title} ({product_tag}), Количество: {quantity}')
            else:
                products_info.append('Товар не найден')
        
        products_info_str = '\n'.join(products_info)

        # Update the sending status in the database
        db.query('UPDATE orders SET sending = TRUE WHERE order_id = %s', (order_id,))
        await bot.answer_callback_query(callback_query.id, text='Заказ отправлен', show_alert=True)
        
        await bot.send_message(
            callback_query.message.chat.id,
            f'Уважаемый(ая) {usr_name}, ваш заказ №{order_id} с товарами:\n{products_info_str}\n'
            f'передан в доставку на адрес {usr_address}.',
            parse_mode='HTML'
        )

        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)  # Delete the message
    else:
        await bot.answer_callback_query(callback_query.id, text='Данные о заказе не найдены', show_alert=True)