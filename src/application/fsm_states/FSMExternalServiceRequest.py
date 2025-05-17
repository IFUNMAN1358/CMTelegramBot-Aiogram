from aiogram.fsm.state import StatesGroup, State


class FSMExternalServiceRequest(StatesGroup):
    writing_name = State()
    writing_requires_api_key = State()