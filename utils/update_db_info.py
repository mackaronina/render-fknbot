import html
import logging

from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from database import Chat, User


async def update_chat_info(tg_chat: types.Chat, session: AsyncSession) -> None:
    name = html.escape(tg_chat.title)
    logging.info(f'Toxic message in chat {name} with id {tg_chat.id}')
    chat = await session.get(Chat, tg_chat.id)
    if chat is None:
        session.add(Chat(id=tg_chat.id, name=name))
    else:
        chat.name = name
        chat.toxic_level += 1


async def update_user_info(tg_user: types.User, session: AsyncSession, toxicity: float, text: str) -> None:
    name = html.escape(tg_user.full_name)
    text = html.escape(text.replace('\n', ''))
    logging.info(f'Toxic message from user {name} with id {tg_user.id}. Text: {text}')
    if len(text) > 500:
        text = text[:500] + '..'
    user = await session.get(User, tg_user.id)
    if user is None:
        session.add(User(id=tg_user.id, name=name, max_toxic_percent=toxicity, max_toxic_text=text))
    else:
        user.name = name
        user.toxic_level += 1
        user.today_toxic_level += 1
        if toxicity > user.max_toxic_percent:
            user.max_toxic_percent = toxicity
            user.max_toxic_text = text
