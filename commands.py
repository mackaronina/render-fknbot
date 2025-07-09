from aiogram import Bot
from aiogram.types import BotCommand


async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command='toxic', description='Узнать насколько чел токсик'),
        BotCommand(command='top', description='Самые токсичные челы'),
        BotCommand(command='rndm', description='Случайная токсичная цитата'),
        BotCommand(command='pet', description='Погладить'),
        BotCommand(command='cube', description='Кубифицировать'),
        BotCommand(command='kill', description='Отбайкрактарить'),
        BotCommand(command='paint', description='Нарисуй пиздатый хуй')
    ]
    await bot.set_my_commands(commands)
