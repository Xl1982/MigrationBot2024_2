
from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from source.single_chat.start_handlers.start_handler import start_work
from source.single_chat.start_handlers.keyboard import get_main_keyboard
from source.bot_init import dp, bot
from source.config import MAIN_ADMIN



#ХЕНДЛЕР ЗАКАЗА ПЕРЕВОДЧИКА
@dp.message_handler(text='Встреча с переводчиком')
async def taxi_command(message: types.Message, state: FSMContext):

    user_id = message.from_user.id
    user_username = message.from_user.username
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Назад'))
    await message.answer(
        "Отлично! Для встречи с переводчиком, пожалуйста, укажите следующую информацию:\nГде встретиться?",
        reply_markup=keyboard)
    await state.set_state("translator:where")
    admin_message = f"Идёт заполнение заявки на встречу с переводчиком!\n\nID: {user_id}\nUsername: @{user_username}"
    await bot.send_message(MAIN_ADMIN, admin_message)


@dp.message_handler(state="translator:where")
async def process_destination(message: types.Message, state: FSMContext):
    destination = message.text
    if destination == "Назад":
        # Возвращаемся к указанию адреса отправления или выходим из режима заполнения заявки
        if await state.get_state() == "translator:where":
            # Выходим из режима заполнения заявки
            await start_work(message) # Вызываем функцию начала работы
            # Сбрасываем состояние пользователя
            await state.finish()
        else:
            # Возвращаемся к указанию адреса отправления
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Назад'))
            await message.answer("Вы вернулись на предыдущий шаг. Где встретится?", reply_markup=keyboard)
            await state.set_state("translator:where")
    else:
        # Сохраняем адрес назначения и переходим к следующему этапу
        await state.update_data(destination=destination)
        await message.answer("Укажите дату и время встречи?")
        await state.set_state("translator:what_time")


@dp.message_handler(state="translator:what_time")
async def process_time(message: types.Message, state: FSMContext):
    time = message.text
    if time == "Назад":
        # Возвращаемся к указанию адреса назначения или выходим из режима заполнения заявки
        if await state.get_state() == "translator:where":
            # Выходим из режима заполнения заявки
            await start_work(message) # Вызываем функцию начала работы
            # Сбрасываем состояние пользователя
            await state.finish()
        else:
            # Возвращаемся к указанию адреса назначения
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Назад'))
            await message.answer("Вы вернулись на предыдущий шаг. Укажите место встречи?", reply_markup=keyboard)
            await state.set_state("translator:where")
    else:
        # Сохраняем время встречи и переходим к следующему этапу
        await state.update_data(time=time)
        await message.answer("Введите ваш номер телефона для связи?")
        await state.set_state("translator:number_phone")


@dp.message_handler(state="translator:number_phone")
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text
    if phone == "Назад":
        # Возвращаемся к указанию даты и времени поездки или выходим из режима заполнения заявки
        if await state.get_state() == "translator:where":
            # Выходим из режима заполнения заявки
            await start_work(message) # Вызываем функцию начала работы
            # Сбрасываем состояние пользователя
            await state.finish()
        else:
            # Возвращаемся к указанию даты и времени встречи
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Назад'))
            await message.answer("Вы вернулись на предыдущий шаг. Введите время и дату встречи?", reply_markup=keyboard)
            await state.set_state("translator:what_time")
    else:
        # Сохраняем номер телефона и завершаем заполнение заявки
        await state.update_data(phone=phone)
        user_data = await state.get_data()

        # Отправка сообщения админу с информацией о заказе
        admin_message = f"Новый заказ встречи с переводчиком!\n\n" \
                        f"Где: {user_data['destination']}\n" \
                        f"Время: {user_data['time']}\n" \
                        f"Телефон: {user_data['phone']}\n"

        await bot.send_message(MAIN_ADMIN, admin_message)
        # Сброс состояния пользователя
        await state.finish()

        # Возвращение кнопок выбора услуг
        markup = get_main_keyboard()  # Используем функцию для получения клавиатуры
        await message.answer("Ваш заказ встречи с переводчиком успешно оформлен! Что еще вас интересует?", reply_markup=markup)


