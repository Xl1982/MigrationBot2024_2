from aiogram import types

from source.config import MAIN_ADMIN, ADMIN_LINK
from source.bot_init import dp, bot

from datetime import datetime, timedelta
from aiogram.types import ChatPermissions

# Создаем словарь для хранения информации о пользователях
user_data = {}


@dp.message_handler(lambda message: message.chat.type in (types.ChatType.SUPERGROUP, types.ChatType.GROUP),
                    content_types=types.ContentType.ANY, is_forwarded=True)
async def handle_forwarded_message(message: types.Message):
    # Проверяем, является ли отправитель администратором
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    admin_mention = (await bot.get_chat_member(message.chat.id, MAIN_ADMIN)).user.get_mention(as_html=True)
    
    # !!! Пофиксить условия
    if member.is_chat_admin() or (member.user.first_name == 'Group' and member.user.mention == '@GroupAnonymousBot'):
        pass
    else:
        # Получаем информацию о пользователе из словаря
        user_id = message.from_user.id
        if user_id in user_data:
            user_info = user_data[user_id]
        else:
            user_info = {'message_count': 0, 'last_message_time': None}
        
        now = datetime.now()
        if user_info['last_message_time'] and (now - user_info['last_message_time']) < timedelta(minutes=3):
            user_info['message_count'] += 1
            if user_info['message_count'] > 2:
                # Применяем ограничения на отправку сообщений
                permissions = ChatPermissions(can_send_messages=False)
                await bot.restrict_chat_member(message.chat.id, user_id, 
                                               until_date=now + timedelta(days=1),
                                               permissions=permissions)
                # Создаем упоминание пользователя
                user_mention = message.from_user.get_mention(as_html=True)
                # Отправляем сообщение с упоминаниями
                await message.reply(f"{user_mention}, вы отправили слишком много пересланных сообщений "
                                    f"и были ограничены в отправке сообщений на сутки.\n\n"
                                    f"Если вы хотите разместить объявление - скопируйте и отправьте его сюда.\n\n"
                                    f"В случае возникновения проблем свяжитесь с администратором: {ADMIN_LINK}")
                return
        else:
            user_info['message_count'] = 1
        user_mention = message.from_user.get_mention(as_html=True)
        user_info['last_message_time'] = now
        user_data[user_id] = user_info

        # Удаляем пересланное сообщение
        await message.delete()
        # Отправляем сообщение о нарушителе с его user_id
        await bot.send_message(message.chat.id, f"Пользователь с user_id {user_id} ({user_mention}) переслал сообщение из другой группы, "
                                f"что запрещено.\n\n"
                                f"Если вы хотите разместить объявление - скопируйте и отправьте его сюда.\n\n"
                                f"В случае возникновения проблем свяжитесь с администратором: {ADMIN_LINK}")
