import json
from typing import Optional

from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup

from src.application.fsm_states.FSMLogin import FSMLogin
from src.domain.endpoints.CMEndpoints import cm_endpoints
from src.domain.model.Session import Session
from src.domain.service.RequestService import request_service
from src.infrastructure.configuration.persistense.RedisConnection0Client import redis_0_client
from src.infrastructure.configuration.properties.CMProperties import cm_properties

auth_router = Router()

#
# Command: /auth - Аутентификация
#

@auth_router.message(Command("auth"))
async def command_auth(message: Message):
    redis = redis_0_client.get_client()

    opt_str_session: Optional[str] = await redis.hget("sessions", f"session:{message.from_user.id}")

    row = [[InlineKeyboardButton(text="Вход", callback_data="login")]]
    if opt_str_session is not None:
        row.append([InlineKeyboardButton(text="Выход", callback_data="logout")])

    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=row, resize_keyboard=True)
    await message.answer(text="Аутентификация:", reply_markup=inline_keyboard)

#
# CallbackQuery: login
#

@auth_router.callback_query(StateFilter(None), F.data == "login")
async def callback_query_login(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=None
    )
    await call.message.answer(text="Введите имя пользователя:")
    await state.set_state(FSMLogin.writing_username)

# writing username

@auth_router.message(FSMLogin.writing_username, F.text)
async def receiving_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text.strip())
    await message.answer(text="Введите пароль:")
    await state.set_state(FSMLogin.writing_password)

# writing password

@auth_router.message(FSMLogin.writing_password, F.text)
async def receiving_password(message: Message, state: FSMContext):
    try:
        redis = redis_0_client.get_client()

        await state.update_data(password=message.text.strip())
        auth_dct = await state.get_data()
        await state.clear()

        messages_for_delete = list()
        for i in range(message.message_id - 4, message.message_id + 1):
            messages_for_delete.append(i)
        await message.bot.delete_messages(message.chat.id, messages_for_delete)

        result = await request_service.post(
            url=cm_endpoints.POST_api_external_v1_auth_login(),
            json={
                "username": auth_dct.get("username"),
                "password": auth_dct.get("password")
            },
            headers={
                "Content-Type": "application/json",
                "X-Service-Name": cm_properties.get_cm_bot_x_service_name(),
                "X-API-Key": cm_properties.get_cm_bot_x_api_key()
            }
        )

        if result["success"]:

            session = Session.from_dict(result["data"])

            if not session.get_user_roles().__contains__("ROLE_ADMIN"):
                await message.answer("У вас недостаточно прав для пользования этим сервисом")
                return

            json_session = json.dumps(session.to_dict())
            await redis.hset("sessions", f"session:{message.from_user.id}", json_session)

            await message.answer(f"Добро пожаловать, {session.get_first_name()}")
        else:
            await message.answer(result["error"])

    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

#
# CallbackQuery: logout
#

@auth_router.callback_query(F.data == "logout")
async def callback_query_logout(call: CallbackQuery):
    await call.answer()
    redis = await redis_0_client.get_client()
    await redis.hdel("sessions", f"session:{call.from_user.id}")
    await call.message.answer(text="Вы вышли из аккаунта")
    await call.bot.delete_message(call.message.chat.id, call.message.message_id)