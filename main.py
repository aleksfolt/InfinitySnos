import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
from handlers.admin import mass_router
from handlers.back import back_router
from handlers.bot_net_handler import bot_net_router
from handlers.history_handler import history_router
from handlers.mail_handler import mail_router
from handlers.report_handler import report_router
from handlers.start_handler import start_router
from middlewares.isbaned import BannedMiddleware


async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(start_router, report_router, history_router, bot_net_router, back_router, mail_router, mass_router)
    dp.message.middleware(BannedMiddleware())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
