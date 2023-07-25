from aiogram import types

from source.config import ADMIN_LINK
from source.bot_init import dp, bot

# Функция-обработчик для пересланных сообщений
@dp.message_handler(lambda message: message.chat.type in (types.ChatType.SUPERGROUP, types.ChatType.GROUP),
                    content_types=types.ContentType.ANY, is_forwarded=True)
async def handle_forwarded_message(message: types.Message):
    # Проверяем, является ли отправитель администратором
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    
    if not member.is_chat_admin():
        # Удаляем пересланное сообщение
        await message.delete()
        # Отправляем ссылку на администратора
        await bot.send_message(message.chat.id, f"Пересылать сообщения из других групп запрещено." 
                                " Если вы хотите разместить объявление - скопируйте и отправьте его сюда.\n\n"
                                f"В случае возникновения проблем свяжитесь с администратором: {ADMIN_LINK}")