import asyncio

from aiogram import types

from source.bot_init import bot, dp


count_messages = 0


async def restart_count_messages(seconds):
    print('Таймаут на приветствия')
    await asyncio.sleep(seconds)
    global count_messages
    print("Окончания таймаута на приветствия")
    count_messages = 0
    

# Обработчик события присоединения нового участника к группе
@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def welcome_new_member(message: types.Message):
    # Получаем информацию о первом новом участнике
    new_member = message.new_chat_members[0]

    global count_messages

    if count_messages < 3:
        # Приветственное сообщение для нового участника
        welcome_text = (f"Поприветствуем нового пользователя!👋\nHola {new_member.first_name}! 👋\nРасскажи о себе, чем занимаешься, чем интересуешься?\n"
        "Прочти пожалуйста правила группы в закрепе\nhttps://t.me/torrevieja_migration/727")

        # Отправляем приветственное сообщение новому участнику
        await message.reply(welcome_text)
        count_messages += 1
        if count_messages == 3:
            await restart_count_messages(1800)
    # Устанавливаем таймаут в одну минуту
    await asyncio.sleep(60)
    