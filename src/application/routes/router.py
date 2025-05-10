from aiogram import Router

from start import start_router

router = Router()
router.include_routers(start_router)