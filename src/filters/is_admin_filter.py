from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from config import OWNER_IDS


class IsAdminFilter(BaseFilter):
    def __init__(self, should_be_admin: bool = True):
        self.should_be_admin = should_be_admin

    async def __call__(self, event: Union[Message, CallbackQuery], *args, **kwargs) -> bool:
        # получать id админов из csv
        admin_ids = []
        flag = event.from_user.id in [*OWNER_IDS, admin_ids]
        return flag is self.should_be_admin
