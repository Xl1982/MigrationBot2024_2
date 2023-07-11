from aiogram import types
from aiogram.utils.exceptions import BotBlocked, CantInitiateConversation

from datetime import datetime, timedelta

from source.bot_init import dp, bot
from source.config import ADMIN_LINK


def mute_permissions():
    permissions = types.ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_polls=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
    can_change_info=False,
    can_invite_users=False,
    can_pin_messages=False
    )
    return permissions


def unmute_permissions():
    permissions = types.ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_polls=True,
    can_send_other_messages=True,
    can_add_web_page_previews=False,
    can_change_info=False,
    can_invite_users=True,
    can_pin_messages=False
    )   
    return permissions


# Обработчик команды /ban, которая должна быть ответом на сообщение пользователя
@dp.message_handler(lambda message: message.chat.type in [types.ChatType.GROUP, types.ChatType.SUPERGROUP], 
                    is_reply=True, commands=["ban"])
async def ban_user(message: types.Message):
    # Проверяем, что команда была отправлена администратором чата
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if chat_member.is_chat_admin():
        # Получаем ID пользователя, на которого ответили
        user_id = message.reply_to_message.from_user.id
        # Проверяем, что он не является администратором или владельцем чата
        target_member = await bot.get_chat_member(message.chat.id, user_id)
        if not (target_member.is_chat_admin() or target_member.is_chat_owner()):
            # Исключаем его из чата
            await bot.kick_chat_member(message.chat.id, user_id)
            # Отправляем сообщение об успешном бане
            await message.reply(f"Пользователь {user_id} исключен из чата.\n"
                                f"Чтобы дать ему возможность вернуться в чат, используйте команду \n/unban {user_id}")
        else:
            # Отправляем сообщение об ошибке
            await message.reply("Вы не можете банить администраторов или владельца чата.")
    else:
        # Отправляем сообщение об ошибке
        await message.reply("Вы не можете банить пользователей в этом чате.")


# Обработчик команды /unban, которая принимает ID пользователя в качестве аргумента
@dp.message_handler(lambda message: message.chat.type in [types.ChatType.GROUP, types.ChatType.SUPERGROUP],
                    commands=["unban"])
async def unban_user(message: types.Message):
    # Проверяем, что команда была отправлена администратором чата
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if chat_member.is_chat_admin():
        # Получаем ID пользователя из аргумента
        user_id = message.get_args()
        # Проверяем, что аргумент не пустой
        if user_id:
            # Возвращаем его в чат
            await bot.unban_chat_member(message.chat.id, user_id)
            # Отправляем сообщение об успешном разбане
            await message.reply(f"Пользователь {user_id} может вернуться в чат.")
            # Пытаемся отправить ему уведомление в личные сообщения с ссылкой на чат
            try:
                updated_chat = await bot.get_chat(message.chat.id)
                await bot.send_message(user_id, f"Вы были разбанены в чате {message.chat.title}. Ссылка приглашение - {updated_chat.invite_link}")
            except BotBlocked:
                # Если бот заблокирован пользователем, отправляем сообщение об этом в общий чат
                await message.reply(f"Пользователь {user_id} заблокировал бота и не получил уведомление о разбане.")
            except CantInitiateConversation:
                # Если бот не может начать разговор с пользователем, отправляем сообщение об этом в общий чат
                await message.reply(f"Бот не может начать разговор с пользователем {user_id} и не отправил ему уведомление о разбане.")
        else:
            # Отправляем сообщение с инструкцией по использованию команды
            await message.reply("Чтобы разбанить пользователя, нужно указать его ID в качестве аргумента команды.\n"
                                "Например: /unban 123456789")
    else:
        # Отправляем сообщение об ошибке
        await message.reply("Вы не можете разбанивать пользователей в этом чате.")


# Обработчик команды /mute, которая должна быть ответом на сообщение пользователя
@dp.message_handler(lambda message: message.chat.type in [types.ChatType.GROUP, types.ChatType.SUPERGROUP],
                    is_reply=True, commands=["mute"])
async def mute_user(message: types.Message):
    # Проверяем, что команда была отправлена администратором чата
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if chat_member.is_chat_admin():
        # Получаем ID пользователя, на которого ответили
        user_id = message.reply_to_message.from_user.id
        # Проверяем, что он не является администратором или владельцем чата
        target_member = await bot.get_chat_member(message.chat.id, user_id)
        if not (target_member.is_chat_admin() or target_member.is_chat_owner()):
            # Ограничиваем его права на отправку сообщений на сутки
            until_date = datetime.now() + timedelta(days=1)
            await bot.restrict_chat_member(message.chat.id, user_id, until_date=until_date, permissions=mute_permissions())
            # Отправляем сообщение об успешном мьюте с ссылкой на админа
            await message.reply(f"Пользователь {user_id} замьючен на сутки.\n"
                                f"Чтобы размьютить его раньше, используйте команду /unmute {user_id}\n"
                                f"Если у вас есть вопросы или жалобы по поводу мьюта, обратитесь к [админу]({ADMIN_LINK}).", parse_mode="Markdown")
        else:
            # Отправляем сообщение об ошибке
            await message.reply("Вы не можете мьютить администраторов или владельца чата.")
    else:
        # Отправляем сообщение об ошибке
        await message.reply("Вы не можете мьютить пользователей в этом чате.")


# Обработчик команды /unmute, которая может быть ответом на сообщение пользователя или принимать ID пользователя в качестве аргумента
@dp.message_handler(lambda message: message.chat.type in [types.ChatType.GROUP, types.ChatType.SUPERGROUP],
                    commands=["unmute"])
async def unmute_user(message: types.Message):
    # Проверяем, что команда была отправлена администратором чата
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if chat_member.is_chat_admin():
        # Если команда была ответом на сообщение пользователя
        if message.reply_to_message:
            # Получаем ID пользователя, на которого ответили
            user_id = message.reply_to_message.from_user.id
            # Проверяем, что он не является администратором или владельцем чата
            target_member = await bot.get_chat_member(message.chat.id, user_id)
            if not (target_member.is_chat_admin() or target_member.is_chat_owner()):
                # Возвращаем ему полные права в чате
                await bot.restrict_chat_member(message.chat.id, user_id, permissions=unmute_permissions())
                # Отправляем сообщение об успешном размьюте с упоминанием пользователя
                await message.reply(f"Пользователь {message.reply_to_message.from_user.get_mention(as_html=True)} размьючен.", parse_mode="HTML")
            else:
                # Отправляем сообщение об ошибке
                await message.reply("Вы не можете размьютить администраторов или владельца чата.")
        # Если команда принимает ID пользователя в качестве аргумента
        else:
            # Получаем ID пользователя из аргумента
            user_id = message.get_args()
            # Проверяем, что аргумент не пустой
            if user_id:
                # Возвращаем ему полные права в чате
                await bot.restrict_chat_member(message.chat.id, user_id, types.ChatPermissions(True))
                # Отправляем сообщение об успешном размьюте
                await message.reply(f"Пользователь {user_id} размьючен.")
            else:
                # Отправляем сообщение с инструкцией по использованию команды
                await message.reply("Чтобы размьютить пользователя, нужно ответить на его сообщение командой /unmute или указать его ID в качестве аргумента команды.\n"
                                    "Например: /unmute 123456789")
    else:
        # Отправляем сообщение об ошибке
        await message.reply("Вы не можете размьютить пользователей в этом чате.")
