import os

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types

from source.single_chat.admin_commands.start import info_handler_two
from source.bot_init import bot, dp

class SpamFilterStates(StatesGroup):
    choice = State()  # Состояние выбора действия (добавить или удалить)
    add_word = State()  # Состояние добавления слова
    delete_word = State()  # Состояние удаления слова


@dp.callback_query_handler(lambda c: c.data == 'spam_edit_exit', state="*")
async def exit_spam_edit(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    await state.finish()
    await info_handler_two(query.message) 
                         

@dp.callback_query_handler(lambda c: c.data == 'spam_filter')
async def send_me_new_spam_word(query: types.CallbackQuery):
    await query.answer()
    await bot.delete_message(query.message.chat.id, query.message.message_id)

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("Добавить слово", callback_data="add_word"),
               types.InlineKeyboardButton("Удалить слово", callback_data="delete_word"))
    markup.add(types.InlineKeyboardButton('Выход', callback_data='spam_edit_exit'))
    
    await query.message.answer("Что вы хотите сделать?", reply_markup=markup)
    await SpamFilterStates.choice.set()


@dp.callback_query_handler(Text(equals=["add_word", "delete_word"]), state=SpamFilterStates.choice)
async def choose_action(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выход', callback_data='spam_edit_exit'))
    await state.update_data(action=query.data)
    if query.data == "add_word":
        # Читаем текущие настройки из файла spam_filter.txt с корректной кодировкой
        if os.path.exists('spam_filter.txt'):
            with open('spam_filter.txt', 'r', encoding='utf-8') as file:
                current_settings = file.read()
            if current_settings.strip():
                await query.message.answer(f"Текущие настройки спам-фильтра:\n{current_settings}")
            else:
                await query.message.answer("Текущие настройки спам-фильтра пусты.")
        else:
            await query.message.answer("Текущие настройки спам-фильтра пусты")
        
        await query.message.answer("Пожалуйста, введите слова или предложения через запятую для спам-фильтра:", reply_markup=markup)
        await SpamFilterStates.add_word.set()
    elif query.data == "delete_word":
        # Читаем текущие настройки из файла spam_filter.txt с корректной кодировкой
        if os.path.exists('spam_filter.txt'):
            with open('spam_filter.txt', 'r', encoding='utf-8') as file:
                current_settings = file.read()
            if current_settings.strip():
                await query.message.answer(f"Текущие настройки спам-фильтра:\n{current_settings}")
                await query.message.answer("Пожалуйста, введите слова или предложения через запятую для удаления из спам-фильтра:", reply_markup=markup)
                await SpamFilterStates.delete_word.set()
            else:
                await query.message.answer("Текущие настройки спам-фильтра пусты. Нечего удалять.", reply_markup=markup)
        else:
            await query.message.answer("Текущие настройки спам-фильтра пусты. Нечего удалять.", reply_markup=markup)


@dp.message_handler(state=SpamFilterStates.add_word)
async def process_new_spam_word(message: types.Message, state: FSMContext):
    input_words = message.text.lower().split(',')
    new_words = [word.strip() for word in input_words]
    
    if new_words:
        with open('spam_filter.txt', 'a', encoding='utf-8') as file:
            for word in new_words:
                    file.write(word + '\n')
        
        if len(new_words) == 1:
            await message.answer(f"Слово '{new_words[0]}' добавлено в спам-фильтр.")
        else:
            await message.answer(f"Слова '{', '.join(new_words)}' добавлены в спам-фильтр.")
    else:
        await message.answer("Вы не ввели слова для добавления в спам-фильтр.")
    
    await state.finish()
    await info_handler_two(message)


@dp.message_handler(state=SpamFilterStates.delete_word)
async def process_delete_spam_word(message: types.Message, state: FSMContext):
    input_words = message.text.lower().split(',')
    words_to_delete = [word.strip() for word in input_words]
    
    lines = []
    with open('spam_filter.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    deleted_words = []
    with open('spam_filter.txt', 'w', encoding='utf-8') as file:
        for line in lines:
            if not any(word in line.lower() for word in words_to_delete):
                file.write(line)
            else:
                deleted_words.append(line.strip())
    
    if deleted_words:
        if len(deleted_words) == 1:
            await message.answer(f"Слово '{deleted_words[0]}' удалено из спам-фильтра.")
        else:
            await message.answer(f"Слова '{', '.join(deleted_words)}' удалены из спам-фильтра.")
    else:
        await message.answer("Слова не найдены в списке спам-фильтра.")
    
    await state.finish()
    await info_handler_two(message)




# функция для удаления сообщений содержащих спам-слова
# Загружаем список спам-слов из файла
def get_spam_words():
    spam_words = set()
    if os.path.exists('spam_filter.txt'):
        with open('spam_filter.txt', 'r', encoding='utf-8') as file:
            spam_words = set([line.strip() for line in file.readlines()])
    return spam_words


@dp.message_handler(content_types=types.ContentTypes.ANY, chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def check_spam_and_warn(message: types.Message):
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if not chat_member.is_chat_admin() and chat_member.status != 'left':
        words_in_message = message.text.split()
        for word in words_in_message:
            if word.lower() in get_spam_words():
                # Отправляем предупреждение пользователю
                user_mention = message.from_user.get_mention(as_html=True)
                await message.reply(f"{user_mention}, ваше сообщение содержит запрещенное слово и было удалено.")

                # Удаляем сообщение
                await message.delete()
