from aiogram.fsm.state import State, StatesGroup

class MenuState(StatesGroup):
    main = State()

class RegistrationState(StatesGroup):
    ifo = State()
    address = State()
    phone_number = State()
    comment = State()
    confirm = State()