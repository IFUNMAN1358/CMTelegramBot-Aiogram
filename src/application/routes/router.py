from aiogram import Router

from src.application.routes.auth_router import auth_router
from src.application.routes.external_service_router import external_service_router
from src.application.routes.profile_router import profile_router
from src.application.routes.registration_key_router import registration_key_router
from src.application.routes.start_router import start_router

router = Router()

router.include_routers(
    start_router,
    auth_router,
    external_service_router,
    registration_key_router,
    profile_router
)