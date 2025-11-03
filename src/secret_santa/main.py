import asyncio

from aiogram import Bot, Dispatcher, F
from aioadmin.aiogram.handlers.start import start_handler
from aiogram.filters import Command
from aiogram.types import BotCommand
from aiogram_dialog import setup_dialogs
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from aioadmin.aiogram.router import AdminRouter
from aioadmin.orm.sqlalchemy import SQLAlchemyAdapter

from secret_santa.bot.menu import menu_dialog
from secret_santa.bot.middleware import SessionMiddleware
from secret_santa.bot.registration import registration_dialog
from secret_santa.bot.start import start_router
from secret_santa.config import load_config
from secret_santa.models import Base


async def main() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///santa.db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    config = load_config()

    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, autoflush=False, expire_on_commit=False
    )

    user_bot = Bot(token=config.bot_token_1)
    admin_bot = Bot(token=config.bot_token_2)

    user_dp = Dispatcher()
    admin_dp = Dispatcher()

    user_session_middleware = SessionMiddleware(session_maker=session_maker)
    admin_session_middleware = SessionMiddleware(session_maker=session_maker)

    user_dp.message.middleware.register(user_session_middleware)
    user_dp.callback_query.middleware.register(user_session_middleware)
    admin_dp.message.middleware.register(admin_session_middleware)

    await user_bot.set_my_commands(
        [
            BotCommand(command="start", description="Начать работу с ботом"),
        ]
    )
    await admin_bot.set_my_commands(
        [
            BotCommand(command="admin", description="Админ-панель"),
        ]
    )

    admin_router = AdminRouter(
        name=__name__, adapter=SQLAlchemyAdapter(metadata=Base.metadata, engine=engine)
    )
    admin_router.message.register(start_handler, Command("admin"))
    admin_id = int(config.admin_id)

    admin_dp.include_router(admin_router)

    user_dp.include_router(start_router)
    user_dp.include_router(menu_dialog)
    user_dp.include_router(registration_dialog)
    setup_dialogs(user_dp)

    await asyncio.gather(
        user_dp.start_polling(user_bot),
        admin_dp.start_polling(admin_bot),
    )


def run():
    asyncio.run(main())
