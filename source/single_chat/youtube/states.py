from aiogram.dispatcher.filters.state import State, StatesGroup

class DownloadState(StatesGroup):
    WaitingChoose = State()
    WaitingForLink = State()