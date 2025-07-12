from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.paint import keyboard_paint_start
from utils.images_processing import get_profile_pic, generate_kill_sticker, generate_cube_gif, generate_pet_gif

router = Router()


@router.message(Command('start'))
async def msg_start(message: Message) -> None:
    await message.reply('Я самый клоунский бот на фкн')


@router.message(Command('cube'))
async def msg_cube(message: Message, bot: Bot) -> None:
    profile_pic = await get_profile_pic(message, bot)
    if profile_pic is None:
        return
    gif = await generate_cube_gif(profile_pic)
    if message.reply_to_message is not None:
        await message.reply_to_message.reply_animation(gif)
    else:
        await message.reply_animation(gif)


@router.message(Command('pet'))
async def msg_pet(message: Message, bot: Bot) -> None:
    profile_pic = await get_profile_pic(message, bot)
    if profile_pic is None:
        return
    gif = await generate_pet_gif(profile_pic)
    if message.reply_to_message is not None:
        await message.reply_to_message.reply_animation(gif)
    else:
        await message.reply_animation(gif)


@router.message(Command('kill'))
async def msg_kill(message: Message, bot: Bot) -> None:
    profile_pic = await get_profile_pic(message, bot)
    if profile_pic is None:
        return
    sticker = generate_kill_sticker(profile_pic)
    if message.reply_to_message is not None:
        await message.reply_to_message.reply_sticker(sticker)
    else:
        await message.reply_sticker(sticker)


@router.message(Command('paint'))
async def msg_paint(message: Message) -> None:
    markup = keyboard_paint_start(message.chat.id)
    await message.reply('Нажми на кнопку чтобы отправить свой клоунский рисунок', reply_markup=markup)
