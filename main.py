import asyncio
import logging

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config_data.constants import SCHEDULER_INTERVAL
from keyboards.set_menu import set_main_menu
from config_data.config import config_settings
from handlers import other_handlers, user_handlers, payment_handlers, inline_queries

import logging

from scheduler.tasks import run_broadcasts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=config_settings.tg_bot.token)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_broadcasts, trigger="interval", seconds=SCHEDULER_INTERVAL, args=[bot])
    scheduler.start()

    dp = Dispatcher()

    await set_main_menu(bot)

    dp.include_router(user_handlers.router)
    dp.include_router(payment_handlers.router)
    dp.include_router(inline_queries.router)
    dp.include_router(other_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=['message', 'callback_query', "pre_checkout_query", "successful_payment", "inline_query"])

asyncio.run(main())
