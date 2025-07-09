import html

from aiogram import Router, Bot
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, KICKED, IS_MEMBER, LEFT
from aiogram.types import ChatMemberUpdated, InputFile

router = Router()


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def update_new_member(event: ChatMemberUpdated, bot: Bot) -> None:
    name = html.escape(event.new_chat_member.user.full_name)
    await bot.send_animation(event.chat.id, InputFile('static/images/join.mp4'), caption=name,
                             show_caption_above_media=True)


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_MEMBER >> KICKED))
async def update_kick_member(event: ChatMemberUpdated, bot: Bot) -> None:
    name = html.escape(event.new_chat_member.user.full_name)
    await bot.send_animation(event.chat.id, InputFile('static/images/kick.mp4'), caption=name,
                             show_caption_above_media=True)


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_MEMBER >> LEFT))
async def update_leave_member(event: ChatMemberUpdated, bot: Bot) -> None:
    name = html.escape(event.new_chat_member.user.full_name)
    await bot.send_animation(event.chat.id, InputFile('static/images/leave.mp4'), caption=name,
                             show_caption_above_media=True)
