from __future__ import annotations

from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Start
from aiogram_dialog.widgets.text import Const
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from secret_santa.bot.states import RegistrationState, MenuState
from secret_santa.models import Participant

async def _ensure_not_registered(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    session: AsyncSession = manager.middleware_data["session"]
    user_id = callback.from_user.id

    existing = await session.scalar(
        select(Participant.id).where(Participant.telegram_user_id == user_id)
    )

    if existing:
        await callback.answer(
            "Вы уже зарегистрированы и участвуете в Тайном Санте.",
            show_alert=True,
        )
        return

    await manager.start(RegistrationState.ifo)


menu_dialog = Dialog(
    Window(
        Const('Привет! Я бот "Тайный Санта"'),
        Const("Выбери то, что хочешь сделать!"),
        Button(
            Const("Зарегистрироваться"),
            id="register",
            on_click=_ensure_not_registered,
        ),
        state=MenuState.main,
    )
)