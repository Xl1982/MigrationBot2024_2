from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminGroupState(StatesGroup):
    # Состояния для администраторов в группе
    AdminCommand = State()  # Состояние для обработки команд администратора в группе


class UserGroupState(StatesGroup):
    # Состояния для пользователей в группе
    UserCommand = State()  # Состояние для обработки команд пользователя в группе


class UserPrivateState(StatesGroup):
    # Состояния для пользователей в личных сообщениях
    PrivateCommand = State()  # Состояние для обработки команд пользователя в личных сообщениях


class AdminPrivateState(StatesGroup):
    # Состояния для администраторов в личных сообщениях
    AdminPrivateCommand = State()  # Состояние для обработки команд администратора в личных сообщениях

class TranslatorMeeting(StatesGroup):
    waiting_date = State()
    waiting_location = State()
    waiting_requirements = State()

class DownloadState(StatesGroup):
    WaitingForLink = State()
