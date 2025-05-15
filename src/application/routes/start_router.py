from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

start_router = Router()

#
# Command: /start - Описание
#

@start_router.message(Command("start"))
async def command_start(message: Message):
    await message.answer("Привет!")