from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from src.application.fsm_states.FSMAuth import FSMAuth
from src.domain.endpoints.CMEndpoints import CMEndpoints
from src.infrastructure.configuration.properties.CMProperties import CMProperties

start_router = Router()
cm_properties = CMProperties()
cm_endpoints = CMEndpoints()

@start_router.message(Command("start"))
async def say_hello(message: Message):
    row = [[InlineKeyboardButton(text="Вход", callback_data="fsm_auth")]]
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=row, resize_keyboard=True)
    await message.answer(text="Добро пожаловать", reply_markup=inline_keyboard)


@start_router.callback_query(StateFilter(None), F.data == "fsm_auth")
async def fsm_auth(call: CallbackQuery, state: FSMContext):
    await call.bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=None
    )
    await call.message.answer(text="Введите имя пользователя:")
    await state.set_state(FSMAuth.writing_username)

# writing username

@start_router.message(FSMAuth.writing_username, F.text)
async def receiving_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text.strip())
    await message.answer(text="Введите пароль:")
    await state.set_state(FSMAuth.writing_password)

# writing password

@start_router.message(FSMAuth.writing_password, F.text)
async def receiving_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text.strip())
    auth_dct = await state.get_data()
    await message.answer(text=auth_dct.get("username") + " | " + auth_dct.get("password"))
    await state.clear()


# headers = {
#     "Content-Type": "application/json",
#     "X-Service-Name": cm_properties.get_cm_bot_x_service_name(),
#     "X-API-Key": cm_properties.get_cm_bot_x_api_key()
# }
#
# data = {
#     "username": "",
#     "password": ""
# }
#
# try:
#     response = requests.post(
#         url=cm_endpoints.POST_api_external_v1_auth_login(),
#         json=data,
#         headers=headers
#     )
#     response.raise_for_status()
#     response_data = response.json()
#     await message.answer(str(response_data))
# except HTTPError as e:
#     await message.answer(f"HTTP Error: {e.response.status_code} - {e.response.text}")
# except JSONDecodeError:
#     await message.answer("Failed to parse response as JSON")
# except Exception as e:
#     await message.answer(f"Error: {str(e)}")