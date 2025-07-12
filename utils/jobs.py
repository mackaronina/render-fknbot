import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import ChatMemberAdministrator
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from config import NIGHT_STICKER_ID
from database import connection, User, Chat


@connection
async def job_day(bot: Bot, session: AsyncSession) -> None:
    result = await session.execute(
        select(User).where(User.today_toxic_level > 0).order_by(User.today_toxic_level.desc()).limit(1)
    )
    user = result.scalars().one_or_none()
    if user is not None:
        text = f'Сегодня {user.name} перевыполнил норму токсичности'
        logging.info(f'Toxic of the day is {user.name} with id {user.id}. Today toxic level: {user.today_toxic_level}')
    else:
        text = 'Сегодня обошлось без токсиков'
        logging.info('Today without toxics')
    await session.execute(update(User).values(today_toxic_level=0))
    bot_id = (await bot.get_me()).id
    result = await session.execute(select(Chat))
    chats = result.scalars().all()
    for chat in chats:
        try:
            await bot.send_sticker(chat.id, NIGHT_STICKER_ID)
            await bot.send_message(chat.id, text)
            member = await bot.get_chat_member(chat.id, bot_id)
            if not isinstance(member, ChatMemberAdministrator):
                logging.warning(f"Bot doesn't have administrator rights in chat {chat.id}")
                await bot.send_message(chat.id, 'У бота нет админки в этом чате, а должна быть сука')
        except TelegramAPIError:
            logging.warning(f'Message to chat with id {chat.id} not sent')
