import re
from re import search

from aiogram import Router, F
from aiogram.types import Message, ReactionTypeEmoji
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from middlewares.db import DbSessionMiddleware
from utils.analize_toxicity import analize_toxicity
from utils.update_db_info import update_chat_info, update_user_info

router = Router()
router.message.middleware(DbSessionMiddleware())


@router.message(F.text | F.caption, F.chat.type != 'private')
async def msg_text(message: Message, session: AsyncSession) -> None:
    text = message.text or message.caption
    toxicity = await analize_toxicity(text)
    if toxicity > settings.toxic.threshold and message.forward_from is None:
        await message.react([ReactionTypeEmoji(emoji=settings.toxic.reaction)])
        await update_chat_info(message.chat, session)
        await update_user_info(message.from_user, session, toxicity, text)
    if search(r'\bсбу\b', text, re.IGNORECASE):
        await message.reply_sticker(settings.stickers.sbu_file_id)
    elif search(r'\bпоро[хш]', text, re.IGNORECASE) or search(r'\bрошен', text, re.IGNORECASE):
        await message.reply_sticker(settings.stickers.porohobot_file_id)
    elif search(r'\bзеленс', text, re.IGNORECASE) or search(r'\bзелебоб', text, re.IGNORECASE):
        await message.reply_sticker(settings.stickers.zelebot_file_id)
