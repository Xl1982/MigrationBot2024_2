import os
import re

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

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
        await query.message.answer(
            "Вы выбрали действие 'Добавить слово в спам-фильтр'.\n\n"
            "Пожалуйста, введите новые слова или предложения через запятую.\n"
            "Пример: слово1, слово2, фраза1, фраза2\n\n"
            "Текущие настройки спам-фильтра:\n"
            f"<code>{await get_current_spam_settings()}</code>\n\n",
            reply_markup=markup,
            parse_mode="HTML"
        )
        await SpamFilterStates.add_word.set()
        
    elif query.data == "delete_word":
        await query.message.answer(
            "Вы выбрали действие 'Удалить слова из спам-фильтра'.\n\n"
            "Пожалуйста, введите слова или предложения через запятую, которые вы хотите удалить.\n"
            "Пример: слово1, слово2, фраза1, фраза2\n\n"
            "Текущие настройки спам-фильтра:\n"
            f"<code>{await get_current_spam_settings()}</code>\n\n",
            reply_markup=markup,
            parse_mode="HTML"
        )
        await SpamFilterStates.delete_word.set()

async def get_current_spam_settings():
    with open('spam_filter.txt', 'r', encoding='utf-8') as file:
        current_settings = file.read().strip()
        if current_settings:
            return current_settings
        else:
            return "Текущие настройки спам-фильтра пусты."


@dp.message_handler(state=SpamFilterStates.add_word)
async def process_add_word(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        action = data.get("action")
    
    input_words = message.text.lower().split(',')
    edited_words = [word.strip() for word in input_words if word.strip()]
    
    if edited_words:
        if action == "add_word":
            with open('spam_filter.txt', 'a', encoding='utf-8') as file:
                for word in edited_words:
                    file.write(word + '\n')
            await message.answer(
                f"Слова/предложения '{', '.join(edited_words)}' добавлены в спам-фильтр."
            )
            await show_current_spam_settings(message)  # Показать актуальные настройки
    else:
        await message.answer("Вы не ввели слова/предложения для добавления в спам-фильтр.")
    
    await state.finish()
    await info_handler_two(message)

@dp.message_handler(state=SpamFilterStates.delete_word)
async def process_delete_word(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        action = data.get("action")
    
    input_words = message.text.lower().split(',')
    edited_words = [word.strip() for word in input_words if word.strip()]
    
    if edited_words:
        if action == "delete_word":
            lines_to_keep = []
            deleted_words = []
            with open('spam_filter.txt', 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines:
                    if not any(word in line.lower() for word in edited_words):
                        lines_to_keep.append(line)
                    else:
                        deleted_words.append(line.strip())
            with open('spam_filter.txt', 'w', encoding='utf-8') as file:
                file.writelines(lines_to_keep)
            if deleted_words:
                await message.answer(
                    f"Слова/предложения '{', '.join(deleted_words)}' удалены из спам-фильтра."
                )
                await show_current_spam_settings(message)  # Показать актуальные настройки
            else:
                await message.answer("Слова не найдены в списке спам-фильтра.")
    else:
        await message.answer("Вы не ввели слова/предложения для удаления из спам-фильтра.")
    
    await state.finish()
    await info_handler_two(message)

async def show_current_spam_settings(message: types.Message):
    with open('spam_filter.txt', 'r', encoding='utf-8') as file:
        current_settings = file.read().strip()
        if current_settings:
            await message.answer(f"Текущие настройки спам-фильтра:\n{current_settings}")
        else:
            await message.answer("Текущие настройки спам-фильтра пусты.")



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
        
        # Обновляем регулярное выражение после добавления новых слов
        global spam_words_pattern
        spam_words_pattern = generate_spam_regexp()
    else:
        await message.answer("Вы не ввели слова для добавления в спам-фильтр.")
    
    await state.finish()
    await info_handler_two(message)


@dp.message_handler(state=SpamFilterStates.delete_word)
async def process_delete_spam_word(message: types.Message, state: FSMContext):
    input_words = message.text.lower().split(',')
    words_to_delete = [word.strip() for word in input_words]
    
    lines_to_keep = []
    deleted_words = []
    
    with open('spam_filter.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        
        for line in lines:
            if not any(word in line.lower() for word in words_to_delete):
                lines_to_keep.append(line)
            else:
                deleted_words.append(line.strip())
    
    with open('spam_filter.txt', 'w', encoding='utf-8') as file:
        file.writelines(lines_to_keep)
    
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


# Чтение запрещенных слов из файла spam_filter.txt
def get_spam_words():
    with open('spam_filter.txt', 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

# Функция для формирования регулярного выражения
def generate_spam_regexp():
    spam_words = get_spam_words()
    return re.compile(r'\b(?:' + '|'.join(map(re.escape, spam_words)) + r')\b', re.IGNORECASE)

class NotAdminOrLeftChat(BoundFilter):
    async def check(self, message: types.Message):
        chat_member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        return not chat_member.is_chat_admin() and chat_member.status != 'left'


@dp.message_handler(NotAdminOrLeftChat(),
    content_types=types.ContentTypes.ANY, 
    chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP],
    run_task=True)
async def check_spam_and_warn(message: types.Message):
    spam_words = get_spam_words()  # Получаем список запрещенных слов
    if spam_words:
        spam_regexp = generate_spam_regexp()  # Компилируем регулярное выражение
        if re.search(spam_regexp, message.text):
            # Отправляем предупреждение пользователю
            user_mention = message.from_user.get_mention(as_html=True)
            await message.reply(f"{user_mention}, ваше сообщение содержит запрещенное слово и было удалено.")

            # Удаляем сообщение
            await message.delete()
    else:
        # В случае отсутствия запрещенных слов, просто игнорируем сообщение
        pass
