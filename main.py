import asyncio
import logging

from aiogram import Bot, Dispatcher

from db.base_model import register_models
from keyboards.set_menu import set_main_menu
from config_data.config import config_settings
from handlers import other_handlers, user_handlers, payment_handlers, inline_queries


async def main():
    logger = logging.getLogger(__name__) # pylint: disable=unused-variable

    bot = Bot(token=config_settings.tg_bot.token)
    dp = Dispatcher()

    await set_main_menu(bot)

    dp.include_router(user_handlers.router)
    dp.include_router(payment_handlers.router)
    dp.include_router(inline_queries.router)
    dp.include_router(other_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=['message', 'callback_query', "pre_checkout_query", "successful_payment", "inline_query"])

asyncio.run(main())
