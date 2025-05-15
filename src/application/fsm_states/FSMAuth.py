from aiogram.fsm.state import StatesGroup, State


class FSMAuth(StatesGroup):
    writing_username = State()
    writing_password = State()