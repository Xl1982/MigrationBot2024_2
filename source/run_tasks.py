import asyncio
import os

from source.data.classes.add_chat import ChatManager
from source.group_chat.sending_messages.weather_send_in_group import check_weather_time
from source.group_chat.sending_messages.purchase_currency import send_purchase_currency_notification
from source.group_chat.sending_messages.current_currency import send_currency_notification
from source.group_chat.sending_messages.send_text_messages import send_text_messages

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)  

tasks = []

def create_tasks():
    global tasks
    global loop
 
    path = os.path.join('source', 'data', 'chats.json')
    chat_manager = ChatManager(path)  
    chats = chat_manager.get_all_chat_ids()
    for chat_id in chats:
        chat_info = chat_manager.get_chat_data(chat_id)
        if chat_info['send_weather']:
            tasks.append(loop.create_task(check_weather_time(chat_id)))
        if chat_info['send_currency']:
            tasks.append(loop.create_task(send_currency_notification(chat_id)))
        if chat_info['send_purchase_currency']:
            tasks.append(loop.create_task(send_purchase_currency_notification(chat_id)))
        tasks.append(loop.create_task(send_text_messages(chat_id)))
            

