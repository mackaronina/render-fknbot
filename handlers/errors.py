import html
import logging
import traceback

from aiogram import Router, Bot
from aiogram.types import ErrorEvent, BufferedInputFile

from config import REPORT_CHAT_ID

router = Router()


@router.error()
async def error_handler(event: ErrorEvent, bot: Bot) -> None:
    await bot.send_document(
        REPORT_CHAT_ID,
        BufferedInputFile(traceback.format_exc().encode('utf8'), filename='error.txt'),
        caption=html.escape(str(event.exception)[:500])
    )
    logging.exception(str(event.exception))
