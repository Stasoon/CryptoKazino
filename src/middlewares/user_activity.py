from datetime import datetime
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.database.users import update_last_activity


class UserActivityMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if hasattr(event, 'from_user'):
            try:
                user_id = event.from_user.id
                current_time = datetime.now()
                update_last_activity(user_id=user_id, new_activity_timestamp=current_time)
            except Exception:
                pass

        await handler(event, data)
