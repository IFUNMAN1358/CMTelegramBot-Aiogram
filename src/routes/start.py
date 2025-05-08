from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

start_router = Router()

@start_router.message(F.text)
async def say_hello(message: Message):
    await message.answer(
        message.text
    )