from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

start_router = Router()

@start_router.message(Command("start"))
async def say_hello(message: Message):
    await message.answer("xd")