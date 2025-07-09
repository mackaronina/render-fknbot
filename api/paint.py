import logging

from aiogram import Bot
from aiogram.types import BufferedInputFile
from fastapi import APIRouter, UploadFile, Depends
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from utils.depends import get_bot

router = APIRouter(prefix='/paint')
templates = Jinja2Templates(directory='templates')


@router.post('/send/{chat_id}')
async def send_paint(chat_id: int, file: UploadFile, bot: Bot = Depends(get_bot)) -> dict:
    content = await file.read()
    await bot.send_photo(chat_id, BufferedInputFile(content, filename='paint.png'))
    logging.info(f'Image from webapp sent to {chat_id}')
    return {'message': 'ok'}


@router.get('/')
async def get_paint(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(name='paint.html', context={'request': request})
