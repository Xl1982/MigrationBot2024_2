from aiogram.types import Message
from aiogram.dispatcher.filters import BoundFilter

from source.config import MAIN_ADMIN, MARKET_ADMINS
from source.data.classes.admin_manager import AdminsManager

class IsUser(BoundFilter):
    async def check(self, message: Message):
        return message.from_user.id not in MARKET_ADMINS


class IsAdmin(BoundFilter):
    async def check(self, message: Message):
        return message.from_user.id in MARKET_ADMINS
