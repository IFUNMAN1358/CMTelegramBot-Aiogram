import json
from typing import Optional

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.application.fsm_states.FSMExternalServiceRequest import FSMExternalServiceRequest
from src.application.keyboards.inline_keyboards.external_services_keyboard import build_services_keyboard, \
    fetch_services, ServicePagination
from src.domain.endpoints.CMEndpoints import cm_endpoints
from src.domain.service.RequestService import request_service
from src.infrastructure.configuration.persistense.RedisConnection0Client import redis_0_client
from src.infrastructure.configuration.properties.CMProperties import cm_properties

external_service_router = Router()

#
# Command: /external_service - Внешние сервисы
#

@external_service_router.message(Command("external_service"))
async def command_external_service(message: Message):
    try:
        redis = redis_0_client.get_client()
        opt_str_session: Optional[str] = await redis.hget("sessions", f"session:{message.from_user.id}")

        if opt_str_session is None:
            await message.answer("Войдите в аккаунт, чтобы воспользоваться этими функциями")
            return

        inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Получить список", callback_data="find_all_external_services")],
            [InlineKeyboardButton(text="Создать", callback_data="create_external_service")]
        ])
        await message.answer(text="Внешние сервисы:", reply_markup=inline_keyboard)
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

# CREATE ES
# CallbackQuery: create_external_service
#

@external_service_router.callback_query(StateFilter(None), F.data == "create_external_service")
async def callback_query_create_external_service(call: CallbackQuery, state: FSMContext):
    await call.answer()
    try:
        redis = redis_0_client.get_client()
        opt_str_session: Optional[str] = await redis.hget("sessions", f"session:{call.from_user.id}")

        if opt_str_session is None:
            await call.message.answer("Войдите в аккаунт, чтобы воспользоваться этими функциями")
            return

        await call.message.answer(text="Введите название внешнего сервиса:")
        await state.set_state(FSMExternalServiceRequest.writing_name)
    except Exception as e:
        await call.message.answer(f"Ошибка: {str(e)}")

# writing name

@external_service_router.message(FSMExternalServiceRequest.writing_name, F.text)
async def receiving_name(message: Message, state: FSMContext):
    try:
        redis = redis_0_client.get_client()
        opt_str_session: Optional[str] = await redis.hget("sessions", f"session:{message.from_user.id}")

        if opt_str_session is None:
            await message.answer("Войдите в аккаунт, чтобы воспользоваться этими функциями")
            return

        await state.update_data(name=message.text.strip())
        await message.answer(text="Укажите, требуется ли ключ внешнему сервису (y/N):")
        await state.set_state(FSMExternalServiceRequest.writing_requires_api_key)
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

# writing requires api key

@external_service_router.message(FSMExternalServiceRequest.writing_requires_api_key, F.text)
async def receiving_requires_api_key(message: Message, state: FSMContext):
    try:
        redis = redis_0_client.get_client()
        opt_str_session: Optional[str] = await redis.hget("sessions", f"session:{message.from_user.id}")
        if opt_str_session is None:
            await message.answer("Войдите в аккаунт, чтобы воспользоваться этими функциями")
            return
        access_token = json.loads(opt_str_session).get("accessToken")

        await state.update_data(requires_api_key=message.text.strip())
        auth_dct = await state.get_data()
        requires_api_key = False
        if auth_dct["requires_api_key"] == "y":
            requires_api_key=True
        await state.clear()

        result = await request_service.post(
            url=cm_endpoints.POST_api_external_service(),
            json={
                "name": auth_dct["name"],
                "requiresApiKey": requires_api_key
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
                "X-Service-Name": cm_properties.get_cm_bot_x_service_name(),
                "X-API-Key": cm_properties.get_cm_bot_x_api_key()
            }
        )

        if result["success"]:
            await message.answer(
                text=(f"Сервис создан.\n\n"
                      f"Внешний сервис:\n\n"
                      f"ID:  {result["data"]["id"]}\n"
                      f"Название:  {result["data"]["name"]}\n"
                      f"Ключ:  {result["data"]["apiKey"]}\n"
                      f"Требует ключ:  {result["data"]["requiresApiKey"]}")
            )
        else:
            await message.answer(result["error"])
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

# FIND ALL ESS
# CallbackQuery: find_all_external_services
#

@external_service_router.callback_query(F.data == "find_all_external_services")
async def callback_query_find_all_external_services(call: CallbackQuery):
    await call.answer()
    try:
        redis = redis_0_client.get_client()
        opt_str_session: Optional[str] = await redis.hget("sessions", f"session:{call.from_user.id}")

        if opt_str_session is None:
            await call.message.answer("Войдите в аккаунт, чтобы воспользоваться этими функциями")
            return

        if not opt_str_session:
            raise ValueError("Session data is empty")
        session_data = json.loads(opt_str_session)
        if not isinstance(session_data, dict):
            raise ValueError("Session data is not a valid dictionary")
        access_token = session_data.get("accessToken")
        if not access_token:
            raise ValueError("Access token not found in session data")

        list_services = await fetch_services(access_token)
        if list_services:
            keyboard = build_services_keyboard(list_services, page=1)
            await call.message.edit_reply_markup(reply_markup=keyboard)
        else:
            await call.message.answer("Список сервисов пуст")

    except json.JSONDecodeError:
        await call.message.answer("Ошибка: Неверный формат данных сессии")
    except ValueError as ve:
        await call.message.answer(f"Ошибка: {str(ve)}")
    except Exception as e:
        await call.message.answer(f"Ошибка: {str(e)}")

@external_service_router.callback_query(ServicePagination.filter())
async def pagination_handler(call: CallbackQuery, callback_data: ServicePagination):
    await call.answer()
    try:
        redis = redis_0_client.get_client()
        opt_str_session: Optional[str] = await redis.hget("sessions", f"session:{call.from_user.id}")

        if opt_str_session is None:
            await call.message.answer("Войдите в аккаунт, чтобы воспользоваться этими функциями")
            return

        if not opt_str_session:
            raise ValueError("Session data is empty")
        session_data = json.loads(opt_str_session)
        if not isinstance(session_data, dict):
            raise ValueError("Session data is not a valid dictionary")
        access_token = session_data.get("accessToken")
        if not access_token:
            raise ValueError("Access token not found in session data")

        page = callback_data.page
        list_services = await fetch_services(call.from_user.id, access_token)
        if list_services:
            keyboard = build_services_keyboard(list_services, page=page)
            await call.message.edit_reply_markup(reply_markup=keyboard)
        else:
            await call.message.answer("Список сервисов пуст")

    except json.JSONDecodeError:
        await call.message.answer("Ошибка: Неверный формат данных сессии")
    except ValueError as ve:
        await call.message.answer(f"Ошибка: {str(ve)}")
    except Exception as e:
        await call.message.answer(f"Ошибка: {str(e)}")

# SELECTED ES
# CallbackQuery: selected_external_service:{service_name}
#

@external_service_router.callback_query(lambda c: c.data.startswith("selected_external_service:"))
async def callback_query_selected_external_service(call: CallbackQuery):
    await call.answer()
    try:
        redis = redis_0_client.get_client()
        opt_str_session: Optional[str] = await redis.hget("sessions", f"session:{call.from_user.id}")

        if opt_str_session is None:
            await call.message.answer("Войдите в аккаунт, чтобы воспользоваться этими функциями")
            return

        access_token = json.loads(opt_str_session).get("accessToken")

        service_name = call.data.split(":", 1)[1]
        if not service_name:
            raise ValueError("Service name is empty")

        result = await request_service.get(
            url=cm_endpoints.GET_api_external_service(service_name),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
                "X-Service-Name": cm_properties.get_cm_bot_x_service_name(),
                "X-API-Key": cm_properties.get_cm_bot_x_api_key()
            }
        )

        if result["success"]:
            inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Изменить ключ", callback_data=f"change_api_key_external_service:{service_name}")],
                [InlineKeyboardButton(text="Удалить", callback_data=f"delete_api_key_external_service:{service_name}")]
            ])

            inline_builder = InlineKeyboardBuilder()

            if result["data"]["requiresApiKey"]:
                inline_builder.button(text="Изменить ключ", callback_data=f"change_api_key_external_service:{service_name}")
            inline_builder.button(text="Удалить", callback_data=f"delete_api_key_external_service:{service_name}")

            await call.message.answer(
                text=(f"Внешний сервис:\n\n"
                      f"ID:  {result["data"]["id"]}\n"
                      f"Название:  {result["data"]["name"]}\n"
                      f"Ключ:  {result["data"]["apiKey"]}\n"
                      f"Требует ключ:  {result["data"]["requiresApiKey"]}"),
                reply_markup=inline_builder.as_markup()
            )
        else:
            await call.message.answer(result["error"])
    except Exception as e:
        await call.message.answer(f"Ошибка: {str(e)}")

# CHANGE ES APIKEY
# CallbackQuery: change_api_key_external_service:{service_name}
#

@external_service_router.callback_query(lambda c: c.data.startswith("change_api_key_external_service:"))
async def callback_query_change_api_key_external_service(call: CallbackQuery):
    await call.answer()
    try:
        redis = redis_0_client.get_client()
        opt_str_session: Optional[str] = await redis.hget("sessions", f"session:{call.from_user.id}")

        if opt_str_session is None:
            await call.message.answer("Войдите в аккаунт, чтобы воспользоваться этими функциями")
            return

        access_token = json.loads(opt_str_session).get("accessToken")

        service_name = call.data.split(":", 1)[1]
        if not service_name:
            raise ValueError("Service name is empty")

        result = await request_service.patch(
            url=cm_endpoints.PATCH_api_external_service(service_name),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
                "X-Service-Name": cm_properties.get_cm_bot_x_service_name(),
                "X-API-Key": cm_properties.get_cm_bot_x_api_key()
            }
        )

        if result["success"]:
            await call.message.answer(
                (f"Ключ успешно изменён.\n\n"
                 f"Внешний сервис:\n\n"
                 f"ID:  {result["data"]["id"]}\n"
                 f"Название:  {result["data"]["name"]}\n"
                 f"Ключ:  {result["data"]["apiKey"]}\n"
                 f"Требует ключ:  {result["data"]["requiresApiKey"]}")
            )
        else:
            await call.message.answer(result["error"])
    except Exception as e:
        await call.message.answer(f"Ошибка: {str(e)}")

# DELETE ES
# CallbackQuery: delete_api_key_external_service:{service_name}
#

@external_service_router.callback_query(lambda c: c.data.startswith("delete_api_key_external_service:"))
async def callback_query_delete_api_key_external_service(call: CallbackQuery):
    await call.answer()
    try:
        redis = redis_0_client.get_client()
        opt_str_session: Optional[str] = await redis.hget("sessions", f"session:{call.from_user.id}")

        if opt_str_session is None:
            await call.message.answer("Войдите в аккаунт, чтобы воспользоваться этими функциями")
            return

        access_token = json.loads(opt_str_session).get("accessToken")

        service_name = call.data.split(":", 1)[1]
        if not service_name:
            raise ValueError("Service name is empty")

        result = await request_service.delete(
            url=cm_endpoints.DELETE_api_external_service(service_name),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
                "X-Service-Name": cm_properties.get_cm_bot_x_service_name(),
                "X-API-Key": cm_properties.get_cm_bot_x_api_key()
            }
        )

        if result["success"]:
            await call.message.answer("Ключ успешно удалён.")
        else:
            await call.message.answer(result["error"])
    except Exception as e:
        await call.message.answer(f"Ошибка: {str(e)}")