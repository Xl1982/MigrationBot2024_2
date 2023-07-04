
from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from source.start_handlers.keyboard import get_main_keyboard
from source.bot_init import dp, bot
from source.config import MAIN_ADMIN


#ХЕНДЛЕР ЗАКАЗА ТАКСИ
@dp.message_handler(text='Заказать такси')
async def taxi_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_username = message.from_user.username
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Назад'))
    await message.answer(
        "Отлично! Для оформления заказа такси, пожалуйста, укажите следующую информацию:\nОткуда забрать?",
        reply_markup=keyboard)
    await state.set_state("ожидание_откуда")
    admin_message = f"Идёт заполнение заявки на такси!\n\nID: {user_id}\nUsername: @{user_username}"
    await bot.send_message(MAIN_ADMIN, admin_message)


@dp.message_handler(state="ожидание_откуда")
async def process_origin(message: types.Message, state: FSMContext):
    origin = message.text
    await state.update_data(origin=origin)
    await message.answer("Куда поедете?")
    await state.set_state("ожидание_куда")


@dp.message_handler(state="ожидание_куда")
async def process_destination(message: types.Message, state: FSMContext):
    destination = message.text
    await state.update_data(destination=destination)
    await message.answer("Укажите дату и время поездки?")
    await state.set_state("ожидание_время")


@dp.message_handler(state="ожидание_время")
async def process_time(message: types.Message, state: FSMContext):
    time = message.text
    await state.update_data(time=time)
    await message.answer("Введите ваш номер телефона для связи?")
    await state.set_state("ожидание_телефон")


@dp.message_handler(state="ожидание_телефон")
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text
    await state.update_data(phone=phone)
    user_data = await state.get_data()

    # Отправка сообщения админу с информацией о заказе
    admin_message = f"Новый заказ такси!\n\n" \
                    f"Откуда: {user_data['origin']}\n" \
                    f"Куда: {user_data['destination']}\n" \
                    f"Время: {user_data['time']}\n" \
                    f"Телефон: {user_data['phone']}\n"

    await bot.send_message(MAIN_ADMIN, admin_message)
    # Сброс состояния пользователя
    await state.finish()

    # Возвращение кнопок выбора услуг
    markup = get_main_keyboard()  # Используем функцию для получения клавиатуры
    await message.answer("Ваш заказ такси успешно оформлен! Что еще вас интересует?", reply_markup=markup)

    # Сброс состояния пользователя
    await state.finish()

