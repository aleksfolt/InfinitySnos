from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from database.banned import is_user_banned


class BannedMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id

        if is_user_banned(user_id):
            return await event.answer("Вы забанены и не можете использовать этого бота.")

        return await handler(event, data)
