import logging
from typing import Annotated

from aiogram import Bot
from aiogram.types import BufferedInputFile
from aiogram.utils.web_app import safe_parse_webapp_init_data
from fastapi import APIRouter, Depends, Form, File
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, JSONResponse

from config import BOT_TOKEN
from utils.depends import get_bot

router = APIRouter(prefix='/paint')
templates = Jinja2Templates(directory='templates')


@router.post('/send')
async def send_paint(
        chat_id: Annotated[str, Form()],
        init_data: Annotated[str, Form()],
        image: Annotated[bytes, File()],
        bot: Bot = Depends(get_bot)
) -> JSONResponse:
    try:
        safe_parse_webapp_init_data(BOT_TOKEN, init_data)
    except ValueError:
        logging.warning(f'Image from webapp not sent to {chat_id} due to incorrect init data')
        return JSONResponse({'ok': False, 'error': 'Wrong init data'}, 401)
    await bot.send_photo(chat_id, BufferedInputFile(image, filename='paint.png'))
    logging.info(f'Image from webapp sent to {chat_id}')
    return JSONResponse({'ok': True})


@router.get('/')
async def get_paint(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(name='paint.html', context={'request': request})
