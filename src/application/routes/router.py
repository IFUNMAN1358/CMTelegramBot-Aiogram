from aiogram import Router

from src.application.routes.start import start_router

router = Router()
router.include_routers(start_router)