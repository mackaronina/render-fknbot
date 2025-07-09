from aiogram import Dispatcher, Bot
from aiogram.types import Update
from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from config import BOT_TOKEN
from utils.depends import get_bot, get_dp

router = APIRouter(prefix='')


@router.post(f'/{BOT_TOKEN}', include_in_schema=False)
async def webhook(request: Request, bot: Bot = Depends(get_bot), dp: Dispatcher = Depends(get_dp)) -> None:
    update = Update.model_validate(await request.json(), context={'bot': bot})
    await dp.feed_update(bot, update)


@router.get('/')
async def read_root() -> HTMLResponse:
    return HTMLResponse(content='Main page')
