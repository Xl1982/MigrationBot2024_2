from aiogram.types import Message
from aiogram.dispatcher.filters import BoundFilter
from source.config import ADMINS
import asyncio

from aiogram import executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.dispatcher.filters.state import StatesGroup, State
import source.main_handlers.handlers as handlers
import logging
import source.config as config
from source.main_handlers.filters import *
from loader import dp
from aiogram.dispatcher.filters import BoundFilter, AdminFilter
import aiogram
from aiogram.dispatcher.filters import Command

class IsUser(BoundFilter):
    async def check(self, message: Message):
        return message.from_user.id not in ADMINS


class IsAdmin(BoundFilter):
    async def check(self, message: Message):
        return message.from_user.id in ADMINS


class IsGroup(BoundFilter):
    async def check(self, message: Message) -> bool:
        return message.chat.type == 'group'


class IsChannel(BoundFilter):
    async def check(self, message: types.Message):
        if message.forward_from_chat:
            return message.forward_from_chat.type == types.ChatType.CHANNEL

class isPrivate(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.chat.type == types.ChatType.PRIVATE