import json
from typing import Optional

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.domain.model.Session import Session
from src.infrastructure.configuration.persistense.RedisConnection0Client import redis_0_client

profile_router = Router()

#
# Command: /profile - Профиль
#

@profile_router.message(Command("profile"))
async def command_profile(message: Message):
    redis = redis_0_client.get_client()
    opt_str_session: Optional[str] = await redis.hget("sessions", f"session:{message.from_user.id}")

    if opt_str_session is None:
        await message.answer("Войдите в аккаунт, чтобы увидеть данные сессии")
        return

    dict_session = json.loads(opt_str_session)
    session = Session.from_dict(dict_session)

    await message.answer(
        "*Данные вашей сессии*:\n\n"
        f"*TelegramUserId*: {message.from_user.id}\n"
        f"*Имя пользователя*: {session.get_username()}\n"
        f"*Имя*: {session.get_first_name()}\n"
        f"*Фамилия*: {session.get_last_name()}\n"
        f"*Роли*: {session.get_user_roles()}",
        parse_mode="Markdown"
    )