import asyncio
import logging
import os
import sys

# Auto-configure PythonAnywhere HTTP proxy for free tier
if os.path.exists("/etc/pythonanywhere") or os.getenv("PYTHONANYWHERE_SITE"):
    _pa_proxy = "http://proxy.server:3128"
    os.environ["HTTP_PROXY"] = _pa_proxy
    os.environ["HTTPS_PROXY"] = _pa_proxy
    os.environ["http_proxy"] = _pa_proxy
    os.environ["https_proxy"] = _pa_proxy


from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiohttp import web

from config import BOT_TOKEN
from database import init_db
from handlers import setup_routers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# Keep runner reference globally to prevent garbage collection
_runner: web.AppRunner | None = None


async def start_health_check_server() -> None:
    global _runner
    port_env = os.getenv("PORT")
    if not port_env or not port_env.isdigit():
        logger.info("PORT environment variable not set; skipping HTTP health check server.")
        return

    port = int(port_env)

    async def health_handler(request: web.Request) -> web.Response:
        return web.Response(text="OK", status=200)

    app = web.Application()
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)

    _runner = web.AppRunner(app)
    await _runner.setup()
    site = web.TCPSite(_runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health check HTTP server running on port {port}")



async def set_bot_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="progress", description="Check your progress"),
        BotCommand(command="link", description="Get your invite link"),
        BotCommand(command="admin", description="Admin panel"),
        BotCommand(command="data", description="Show user data (admin)"),
    ]
    await bot.set_my_commands(commands)


async def main() -> None:
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set.")
        sys.exit(1)

    await init_db()
    await start_health_check_server()

    session = None
    proxy_url = os.getenv("PROXY_URL") or os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    if not proxy_url and (os.path.exists("/etc/pythonanywhere") or os.getenv("PYTHONANYWHERE_SITE")):
        proxy_url = "http://proxy.server:3128"

    if proxy_url:
        from aiogram.client.session.aiohttp import AiohttpSession
        session = AiohttpSession(proxy=proxy_url)
        logger.info(f"Using HTTP proxy for Telegram API: {proxy_url}")

    bot = Bot(
        token=BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(setup_routers())

    await set_bot_commands(bot)
    logger.info("Bot started. Polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped.")
