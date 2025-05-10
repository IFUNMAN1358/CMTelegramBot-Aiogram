from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

from infrastructure.configuration.Env import Env
from src.application.routes.router import router

env = Env()

bot = Bot(env.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
dp.include_router(router)

async def handle_webhook(request):
    update = await request.json()
    await dp.feed_raw_update(bot=bot, update=update)
    return web.Response()

async def on_startup(app):
    await bot.set_webhook(
        url=env.WEBHOOK_URL,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True
    )

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

def main():
    app = web.Application()
    app.router.add_post(env.WEBHOOK_PATH, handle_webhook)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host=env.LOCAL_ADDRESS, port=env.LOCAL_PORT)

if __name__ == "__main__":
    main()