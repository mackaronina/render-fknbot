from aiogram import Bot, Dispatcher
from fastapi.requests import Request


def get_bot(request: Request) -> Bot:
    return request.app.state.bot


def get_dp(request: Request) -> Dispatcher:
    return request.app.state.dp
