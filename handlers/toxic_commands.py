import html

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from config import TOXIC_LEVEL_TEXTS
from database import User, Chat
from middlewares.db import DbSessionMiddleware

router = Router()
router.message.middleware(DbSessionMiddleware())


@router.message(Command('rndm'))
async def msg_rndm(message: Message, session: AsyncSession) -> None:
    result = await session.execute(
        select(User).where(User.max_toxic_text.is_not(None)).order_by(func.random()).limit(1)
    )
    user = result.scalars().one_or_none()
    if user is not None:
        await message.reply(user.max_toxic_text)


@router.message(Command('top'))
async def msg_top(message: Message, session: AsyncSession) -> None:
    text = 'Эти челы написали больше всего токсичных сообщений. Могут ли они гордиться этим? Несомненно\n\n'
    result = await session.execute(select(User).where(User.toxic_level > 0).order_by(User.toxic_level.desc()).limit(10))
    users = result.scalars().all()
    for i, user in enumerate(users):
        if i == 0:
            text += f'🏆 <b>{user.name}</b>  {user.toxic_level} ☣️\n'
        else:
            text += f'{i + 1}.  {user.name}  {user.toxic_level} ☣️\n'
    result = await session.execute(select(Chat).where(Chat.toxic_level > 0).order_by(Chat.toxic_level.desc()).limit(1))
    chat = result.scalars().one_or_none()
    if chat is not None:
        text += f'\nФортеця токсичного фронту:\n<b>{chat.name}</b>'
    await message.reply(text)


@router.message(Command('toxic'))
async def msg_toxic(message: Message, session: AsyncSession) -> None:
    if message.reply_to_message is not None:
        user_id = message.reply_to_message.from_user.id
        name = html.escape(message.reply_to_message.from_user.full_name)
    else:
        user_id = message.from_user.id
        name = html.escape(message.from_user.full_name)
    text = f'<b>Токсик  {name}</b>\n\n'
    user = await session.get(User, user_id)
    if user is not None:
        toxic_level = user.toxic_level
        max_toxic_text = user.max_toxic_text
        reactions_count = user.reactions_count
    else:
        toxic_level = 0
        max_toxic_text = None
        reactions_count = None
    text += f'Уровень токсичности:  {toxic_level} ☣️\n'
    for limit, level_text in TOXIC_LEVEL_TEXTS.items():
        if toxic_level < limit:
            text += f'Диагноз:  {level_text}\n'
            break
    if max_toxic_text is not None:
        text += f'Самая токсичная цитата:\n<blockquote expandable>{max_toxic_text}</blockquote>\n'
    if reactions_count is not None:
        text += f'Любимая реакция:  {max(reactions_count.items(), key=lambda k_v: k_v[1])[0]}'
    await message.reply(text)
