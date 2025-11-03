from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from secret_santa.bot.states import MenuState

start_router = Router()

@start_router.message(CommandStart())
async def register(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=MenuState.main,
        mode=StartMode.RESET_STACK,
    )