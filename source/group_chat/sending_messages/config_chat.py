import datetime


from source.config import CHAT_ID_TORA

config_chat = {
    'chat_id': CHAT_ID_TORA,
    'weather_message': True,
    'purchase_message': True,
    'money_cource_message': True,
    'text_message': True
}

times_to_send = {
    'purchase_currency':[
        datetime.time(12, 30),
    ],
    'current_currency':[
        datetime.time(10, 0)
    ],
    'text_messages':[
        datetime.time(13, 0),
        datetime.time(16, 0),
    ],
}