from aiogram.types import Message
from aiogram.dispatcher.filters import BoundFilter

from source.config import MAIN_ADMIN
from source.data.classes.admin_manager import AdminsManager
from source.single_chat.admin_commands.start import check_admins

class IsUser(BoundFilter):
    async def check(self, message: Message):
        return message.from_user.id not in check_admins() or message.from_user.id != MAIN_ADMIN


class IsAdmin(BoundFilter):
    async def check(self, message: Message):
        return message.from_user.id in check_admins() or message.from_user.id == MAIN_ADMIN
