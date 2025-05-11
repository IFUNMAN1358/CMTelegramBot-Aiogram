from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

from src.application.routes.router import router
from src.infrastructure.configuration.properties.BotProperties import BotProperties

bot_properties = BotProperties()

bot = Bot(bot_properties.get_bot_token(), default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
dp.include_router(router)

async def handle_webhook(request):
    update = await request.json()
    await dp.feed_raw_update(bot=bot, update=update)
    return web.Response()

async def on_startup(app):
    await bot.set_webhook(
        url=bot_properties.get_bot_webhook_url(),
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True
    )

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

def main():
    app = web.Application()
    app.router.add_post(bot_properties.get_bot_webhook_path(), handle_webhook)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(
        app=app,
        host=bot_properties.get_bot_local_address(),
        port=bot_properties.get_bot_local_port()
    )

if __name__ == "__main__":
    main()