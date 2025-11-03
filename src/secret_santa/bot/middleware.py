from typing import Callable, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

class SessionMiddleware(BaseMiddleware):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self.session_maker = session_maker

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        async with self.session_maker() as session:
            data["session"] = session
            return await handler(event, data)
