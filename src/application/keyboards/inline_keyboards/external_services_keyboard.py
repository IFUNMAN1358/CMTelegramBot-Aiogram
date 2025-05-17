import json
from math import ceil
from typing import List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domain.endpoints.CMEndpoints import cm_endpoints
from src.domain.service.RequestService import request_service
from src.infrastructure.configuration.persistense.RedisConnection0Client import redis_0_client
from src.infrastructure.configuration.properties.CMProperties import cm_properties

class ServicePagination(CallbackData, prefix="pag"):
    action: str
    page: int

def build_services_keyboard(services: List[dict], page: int = 1, per_page: int = 10) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    total_services = len(services)
    total_pages = ceil(total_services / per_page) if total_services > 0 else 1
    page = max(1, min(page, total_pages))

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    current_services = services[start_idx:end_idx]

    for service in current_services:
        builder.row(InlineKeyboardButton(
            text=service["name"],
            callback_data=f"selected_external_service:{service["name"]}"
        ))

    buttons_row = []
    if page > 1:
        buttons_row.append(InlineKeyboardButton(text="<", callback_data=ServicePagination(action="prev", page=page - 1).pack()))
    else:
        buttons_row.append(InlineKeyboardButton(text="-", callback_data="noop"))

    buttons_row.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop"))

    if page < total_pages:
        buttons_row.append(InlineKeyboardButton(text=">", callback_data=ServicePagination(action="next", page=page + 1).pack()))
    else:
        buttons_row.append(InlineKeyboardButton(text="-", callback_data="noop"))

    builder.row(*buttons_row)
    return builder.as_markup()


async def fetch_services(access_token: str) -> List[dict]:
    result = await request_service.get(
        url=cm_endpoints.GET_api_external_services(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "X-Service-Name": cm_properties.get_cm_bot_x_service_name(),
            "X-API-Key": cm_properties.get_cm_bot_x_api_key()
        }
    )

    if not result["success"]:
        raise ValueError(result["error"])

    parsed_data = result["data"]
    if isinstance(parsed_data, list):
        list_services = parsed_data
    elif isinstance(parsed_data, str):
        try:
            parsed_data = json.loads(parsed_data)
            if not isinstance(parsed_data, list):
                raise ValueError("Parsed JSON data is not a list")
            list_services = parsed_data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data format: {str(e)}")
    else:
        raise ValueError("Data is neither a list nor a string")

    return list_services