from __future__ import annotations

from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Cancel, ManagedRadio, Radio, Row
from aiogram_dialog.widgets.text import Const, Format
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from secret_santa.bot.states import RegistrationState
from secret_santa.models import AddressOption, Participant


async def _on_ifo_entered(
    message: Message,
    widget: TextInput,
    manager: DialogManager,
    text: str,
) -> None:
    manager.dialog_data["ifo"] = text.strip()
    await manager.next()


async def _on_address_option_changed(
    event: CallbackQuery,
    widget: ManagedRadio[str],
    manager: DialogManager,
    item_id: str,
) -> None:
    manager.dialog_data["address_option"] = AddressOption(item_id)


async def _on_address_entered(
    message: Message,
    widget: TextInput,
    manager: DialogManager,
    text: str,
) -> None:
    manager.dialog_data["address"] = text.strip()
    await manager.next()


async def _on_phone_entered(
    message: Message,
    widget: TextInput,
    manager: DialogManager,
    text: str,
) -> None:
    manager.dialog_data["phone_number"] = text.strip()
    await manager.next()


async def _on_comment_entered(
    message: Message,
    widget: TextInput,
    manager: DialogManager,
    text: str,
) -> None:
    manager.dialog_data["comment"] = text.strip()
    await manager.next()


async def _on_comment_skipped(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    manager.dialog_data["comment"] = ""
    await manager.next()


async def _on_confirm(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    user = callback.from_user
    session: AsyncSession = manager.middleware_data["session"]

    participant_stmt = select(Participant).where(
        Participant.telegram_user_id == user.id
    )
    participant = await session.scalar(participant_stmt)

    address_option = manager.dialog_data["address_option"]
    if isinstance(address_option, str):
        address_option = AddressOption(address_option)
        manager.dialog_data["address_option"] = address_option

    if participant is None:
        participant = Participant(
            ifo=manager.dialog_data["ifo"],
            telegram_user_id=user.id,
            username=user.username or "",
            address_option=address_option,
            address=manager.dialog_data["address"],
            phone_number=manager.dialog_data["phone_number"],
            comment=manager.dialog_data.get("comment") or None,
        )
        session.add(participant)
    else:
        participant.ifo = manager.dialog_data["ifo"]
        participant.username = user.username or participant.username
        participant.address_option = address_option
        participant.address = manager.dialog_data["address"]
        participant.phone_number = manager.dialog_data["phone_number"]
        participant.comment = manager.dialog_data.get("comment") or None

    await session.commit()
    await manager.done({"participant_id": participant.id})


async def _confirm_getter(
    dialog_manager: DialogManager,
    **kwargs: Any,
) -> dict[str, Any]:
    stored_option = dialog_manager.dialog_data.get("address_option")
    address_option = (
        AddressOption(stored_option)
        if isinstance(stored_option, str)
        else stored_option
    )
    return {
        "ifo": dialog_manager.dialog_data.get("ifo", ""),
        "address_option": address_option.value if address_option else "",
        "address": dialog_manager.dialog_data.get("address", ""),
        "phone_number": dialog_manager.dialog_data.get("phone_number", ""),
        "comment": dialog_manager.dialog_data.get("comment") or "Без комментариев",
    }


async def _address_window_getter(
    dialog_manager: DialogManager,
    **kwargs: Any,
) -> dict[str, Any]:
    context = dialog_manager.current_context()
    widget_state = context.widget_data.setdefault(
        "address_option_radio", AddressOption.PICKUP.value
    )
    option = dialog_manager.dialog_data.setdefault(
        "address_option",
        AddressOption(widget_state),
    )
    if isinstance(option, str):
        option = AddressOption(option)
        dialog_manager.dialog_data["address_option"] = option
    return {
        "address_option": option.value,
        "address_options": [AddressOption.PICKUP, AddressOption.HOME],
    }


registration_dialog = Dialog(
    Window(
        Const(
            "Прекрасно! Нам нужно собрать несколько данных, чтобы ты смог участвовать в Тайном Санте.\n"
            "Напиши, пожалуйста, свое ИФО."
        ),
        TextInput(id="ifo_input", on_success=_on_ifo_entered),
        Cancel(Const("Отмена")),
        state=RegistrationState.ifo,
    ),
    Window(
        Format("Выбери способ доставки подарка и напиши адрес.\nСейчас выбран: {address_option}"),
        Radio(
            checked_text=Format("🔘 {item.value}"),
            unchecked_text=Format("⚪️ {item.value}"),
            id="address_option_radio",
            item_id_getter=lambda item: item.value,
            items=lambda data, **_: data["address_options"],
            on_state_changed=_on_address_option_changed,
        ),
        TextInput(id="address_input", on_success=_on_address_entered),
        Cancel(Const("Отмена")),
        state=RegistrationState.address,
        getter=_address_window_getter,
    ),
    Window(
        Const("Оставь свой номер телефона."),
        TextInput(id="phone_input", on_success=_on_phone_entered),
        Cancel(Const("Отмена")),
        state=RegistrationState.phone_number,
    ),
    Window(
        Const("Есть ли комментарий или пожелание? Напиши его сообщением или пропусти шаг."),
        TextInput(id="comment_input", on_success=_on_comment_entered),
        Row(
            Button(Const("Пропустить"), id="skip_comment", on_click=_on_comment_skipped),
            Cancel(Const("Отмена")),
        ),
        state=RegistrationState.comment,
    ),
    Window(
        Format(
            "Проверь введенные данные:\n"
            "ИФО: {dialog_data[ifo]}\n"
            "Способ доставки: {address_option}\n"
            "Адрес: {dialog_data[address]}\n"
            "Телефон: {dialog_data[phone_number]}\n"
            "Комментарий: {comment}"
        ),
        Row(
            Button(Const("Подтвердить"), id="confirm_registration", on_click=_on_confirm),
            Cancel(Const("Отмена")),
        ),
        state=RegistrationState.confirm,
        getter=_confirm_getter,
    ),
)
