from aiogram.fsm.state import StatesGroup, State


class FSMLogin(StatesGroup):
    writing_username = State()
    writing_password = State()