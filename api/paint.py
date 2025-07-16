import logging
from typing import Annotated

from aiogram import Bot
from aiogram.types import BufferedInputFile
from aiogram.utils.web_app import safe_parse_webapp_init_data
from fastapi import APIRouter, Depends, Form, File, UploadFile
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from config import settings
from keyboards.paint import keyboard_paint_continue
from utils.depends import get_bot

router = APIRouter(prefix='/paint')
templates = Jinja2Templates(directory='templates')


@router.post('/send')
async def send_paint(
        init_data: Annotated[str, Form()],
        image: Annotated[UploadFile, File()],
        bot: Bot = Depends(get_bot)
) -> JSONResponse:
    try:
        data = safe_parse_webapp_init_data(settings.bot_token.get_secret_value(), init_data)
        chat_id = int(data.start_param.split('__')[0])
    except ValueError:
        logging.warning(f'Image from webapp not sent due to incorrect init data')
        return JSONResponse({'ok': False, 'error': 'Wrong init data'}, 401)
    content = await image.read()
    message = await bot.send_photo(chat_id, BufferedInputFile(content, filename='paint.png'))
    await message.edit_reply_markup(reply_markup=keyboard_paint_continue(chat_id, message.photo[-1].file_id))
    logging.info(f'Image from webapp sent to {chat_id}')
    return JSONResponse({'ok': True})


@router.get('/picture/{file_id}')
async def get_paint(file_id: str, bot: Bot = Depends(get_bot)) -> StreamingResponse:
    downloaded_file = await bot.download(file_id)
    return StreamingResponse(downloaded_file, media_type='image/png')


@router.get('/')
async def get_paint(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(name='paint.html', context={'request': request})
