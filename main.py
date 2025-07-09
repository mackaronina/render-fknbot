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
from config import TIME_ZONE, BOT_TOKEN, REPORT_CHAT_ID, WEBHOOK_DOMAIN, HOST, PORT
from database import create_tables
from handlers import commands, toxic_commands, chat_members, errors, messages, reactions
from utils.jobs import job_day


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    await create_tables()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True))
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

    scheduler = AsyncIOScheduler(timezone=TIME_ZONE)
    scheduler.add_job(job_day, 'cron', (bot,), hour=1, minute=1)
    scheduler.start()

    await bot.send_message(REPORT_CHAT_ID, 'Бот запущен')
    await bot.delete_webhook()
    # Uncomment for polling
    # await dp.start_polling(bot)
    await bot.set_webhook(url=f'{WEBHOOK_DOMAIN}/{BOT_TOKEN}',
                          drop_pending_updates=True)
    await uvicorn.Server(uvicorn.Config(app, host=HOST, port=PORT)).serve()


if __name__ == '__main__':
    asyncio.run(main())
