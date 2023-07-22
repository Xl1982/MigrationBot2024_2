from aiogram.types import Message
from aiogram.dispatcher.filters import BoundFilter

from source.config import MAIN_ADMIN
from source.data.classes.admin_manager import AdminsManager
from source.single_chat.admin_commands.start import check_admins

class IsUser(BoundFilter):
    async def check(self, message: Message):
        if message.from_user.id == MAIN_ADMIN:
            return False
        return message.from_user.id not in check_admins()


class IsAdmin(BoundFilter):
    async def check(self, message: Message):
        if message.from_user.id == MAIN_ADMIN:
            return True
        return message.from_user.id in check_admins()
