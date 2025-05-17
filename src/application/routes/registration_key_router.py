from datetime import datetime
import json
from typing import Optional

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from src.domain.endpoints.CMEndpoints import cm_endpoints
from src.domain.service.RequestService import request_service
from src.infrastructure.configuration.persistense.RedisConnection0Client import redis_0_client
from src.infrastructure.configuration.properties.CMProperties import cm_properties

registration_key_router = Router()

#
# Command: /registration_key - Ключи регистрации
#

@registration_key_router.message(Command("registration_key"))
async def command_registration_key(message: Message):
    try:
        redis = redis_0_client.get_client()
        opt_str_session: Optional[str] = await redis.hget("sessions", f"session:{message.from_user.id}")

        if opt_str_session is None:
            await message.answer("Войдите в аккаунт, чтобы воспользоваться этими функциями")
            return

        inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Создать", callback_data="create_registration_key")]
        ])
        await message.answer(text="Ключи регистрации:", reply_markup=inline_keyboard)
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

# CREATE RK
# CallbackQuery: create_registration_key
#

@registration_key_router.callback_query(F.data == "create_registration_key")
async def callback_query_create_registration_key(call: CallbackQuery):
    await call.answer()
    try:
        redis = redis_0_client.get_client()
        opt_str_session: Optional[str] = await redis.hget("sessions", f"session:{call.from_user.id}")

        if opt_str_session is None:
            await call.message.answer("Войдите в аккаунт, чтобы воспользоваться этими функциями")
            return
        access_token = json.loads(opt_str_session).get("accessToken")

        result = await request_service.post(
            url=cm_endpoints.POST_api_registration_key(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
                "X-Service-Name": cm_properties.get_cm_bot_x_service_name(),
                "X-API-Key": cm_properties.get_cm_bot_x_api_key()
            }
        )

        if result["success"]:
            await call.message.answer(
                (f"Ключ регистрации создан:\n\n"
                 f"ID:  {result["data"]["id"]}\n"
                 f"Значение:  {result["data"]["value"]}\n"
                 f"Создан:  {result["data"]["createdAt"]}")
            )
        else:
            await call.message.answer(result["error"])
    except Exception as e:
        await call.message.answer(f"Ошибка: {str(e)}")