import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import settings
from db.session import engine, Base

from handlers import (
    start_router,
    giveaways_router,
    channels_router,
    buttons_router,
    winners_router,
    errors_router,
)


if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

bot = Bot(
    token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(start_router)
dp.include_router(giveaways_router)
dp.include_router(channels_router)
dp.include_router(buttons_router)
dp.include_router(winners_router)
dp.include_router(errors_router)


async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(on_startup())
    dp.run_polling(bot)
