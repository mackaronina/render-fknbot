from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import settings


def keyboard_paint_start(chat_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Рисовать 🎨', url=f'{settings.paint_web_app_url}?startapp={chat_id}'))
    return builder.as_markup()


def keyboard_paint_continue(chat_id: int, file_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='Дорисовать 🎨', url=f'{settings.paint_web_app_url}?startapp={chat_id}__{file_id}'))
    return builder.as_markup()
