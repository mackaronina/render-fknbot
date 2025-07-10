from aiogram import Router, types, F
from aiogram.types import ReactionTypeEmoji
from sqlalchemy.ext.asyncio import AsyncSession

from database import User
from middlewares.db import DbSessionMiddleware

router = Router()
router.message_reaction.middleware(DbSessionMiddleware())


@router.message_reaction(F.chat.type != 'private')
async def msg_reaction(event: types.MessageReactionUpdated, session: AsyncSession) -> None:
    user = await session.get(User, event.user.id)
    if user is not None and len(event.new_reaction) > 0 and isinstance(event.new_reaction[0], ReactionTypeEmoji):
        reaction = event.new_reaction[0].emoji
        if reaction in user.reactions_count:
            user.reactions_count[reaction] += 1
        else:
            user.reactions_count[reaction] = 1
