from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    weather_button = KeyboardButton('Погода')
    exchange_button = KeyboardButton('Курс валют')
    taxi_button = KeyboardButton('Заказать такси')
    translator_button = KeyboardButton('Встреча с переводчиком')
    admin_button = KeyboardButton('Написать админу')
    youtube_button = KeyboardButton('Скачать с youtube')
    autobus_button = KeyboardButton('Расписание автобусов')
    market_button = KeyboardButton('Магазин')
    #pay_button = KeyboardButton('Оплатить')
    # markup.add(weather_button, exchange_button, taxi_button, translator_button, admin_button, pay_button)

    markup.add(weather_button, exchange_button, taxi_button, autobus_button, translator_button, admin_button, youtube_button)
    markup.add(market_button)
    return markup
