import asyncio
import logging

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api import webhook, paint
from commands import set_commands
from config import settings
from database import create_tables
from handlers import commands, toxic_commands, chat_members, errors, messages, reactions
from utils.jobs import job_day


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    await create_tables()

    bot = Bot(token=settings.bot_token.get_secret_value(),
              default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True))
    dp = Dispatcher()
    dp.include_routers(commands.router, toxic_commands.router, chat_members.router, errors.router,
                       messages.router, reactions.router)
    await set_commands(bot)

    app = FastAPI()
    app.mount('/static', StaticFiles(directory='static'), 'static')
    app.include_router(webhook.router)
    app.include_router(paint.router)
    app.state.bot = bot
    app.state.dp = dp

    scheduler = AsyncIOScheduler(timezone=settings.time_zone)
    scheduler.add_job(job_day, 'cron', (bot,), hour=1, minute=1)
    scheduler.start()

    await bot.delete_webhook()
    # Uncomment for polling
    # await dp.start_polling(bot)
    await bot.set_webhook(url=f'{settings.webhook_domain}/{settings.bot_token.get_secret_value()}',
                          drop_pending_updates=True)
    logging.info('Bot started')
    await uvicorn.Server(uvicorn.Config(app, host=settings.host, port=settings.port)).serve()


if __name__ == '__main__':
    asyncio.run(main())
