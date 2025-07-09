import random
from io import BytesIO
from typing import BinaryIO

from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot
from aiogram.types import Message, BufferedInputFile
from bs4 import BeautifulSoup
from curl_cffi import CurlMime, AsyncSession
from petpetgif.saveGif import save_transparent_gif


async def get_profile_pic(message: Message, bot: Bot) -> BinaryIO | None:
    if message.reply_to_message is not None:
        pics = await bot.get_user_profile_photos(message.reply_to_message.from_user.id)
    else:
        pics = await bot.get_user_profile_photos(message.from_user.id)
    if pics.total_count == 0:
        await message.reply('Ава не найдена, иди нахуй короче')
        return None
    return await bot.download(pics.photos[0][-1].file_id)


async def generate_cube_gif(profile_pic: BinaryIO) -> BufferedInputFile:
    direction = random.choice(['left', 'right'])
    data = {
        'target': 1,
        'MAX_FILE_SIZE': 1073741824,
        'speed': 'ufast',
        'bg_color': '000000',
        'direction': direction
    }
    formdata = CurlMime()
    formdata.addpart(
        name='image[]',
        content_type='image/png',
        filename='result.png',
        data=profile_pic.read()
    )
    async with AsyncSession(impersonate='chrome110') as s:
        resp = await s.get('https://en.bloggif.com/cube-3d')
        soup = BeautifulSoup(resp.text, 'lxml')
        token = soup.find('form')['action']
        link = f'https://en.bloggif.com{token}'
        resp = await s.post(link, data=data, multipart=formdata)
        soup = BeautifulSoup(resp.text, 'lxml')
        img = soup.find('a', class_='button gray-button')['href']
        link = f'https://en.bloggif.com{img}'
        resp = await s.get(link)
        return BufferedInputFile(resp.content, filename='cube.gif')


async def generate_pet_gif(profile_pic: BinaryIO) -> BufferedInputFile:
    img = Image.open(profile_pic)
    mean = dominant_color(img)
    frames = 10
    resolution = (256, 256)
    images = []
    base = img.convert('RGBA').resize(resolution)
    for i in range(frames):
        squeeze = i if i < frames / 2 else frames - i
        width = 0.8 + squeeze * 0.02
        height = 0.8 - squeeze * 0.05
        offset_x = (1 - width) * 0.5 + 0.1
        offset_y = (1 - height) - 0.08
        canvas = Image.new('RGBA', size=resolution, color=mean)
        canvas.paste(base.resize((round(width * resolution[0]), round(height * resolution[1]))),
                     (round(offset_x * resolution[0]), round(offset_y * resolution[1])))
        with Image.open(f'static/images/pet{i}.gif').convert('RGBA').resize(
                resolution) as pet:
            canvas.paste(pet, mask=pet)
        images.append(canvas)
    bio = BytesIO()
    save_transparent_gif(images, durations=20, save_file=bio)
    return BufferedInputFile(bio.getvalue(), filename='pet.gif')


def generate_kill_sticker(profile_pic: BinaryIO) -> BufferedInputFile:
    img = Image.open(profile_pic)
    img2 = Image.new(mode='RGBA', size=(900, 900))
    draw = ImageDraw.Draw(img2)
    font = ImageFont.FreeTypeFont('static/fonts/times-new-roman.ttf', size=90)
    draw.multiline_text((450, 450), 'ОТБАЙРАКТАРЕН', fill=(190, 0, 44), anchor='mm', font=font, align='center',
                        spacing=4, stroke_width=4, stroke_fill=(73, 73, 73))
    img2 = img2.rotate(45)
    img = img.convert('L').convert('RGB')
    img.paste(img2, (-130, -130), img2.convert('RGBA'))
    return BufferedInputFile(img.tobytes(), filename='sticker.webp')


async def get_pil(bot: Bot, file_id: str) -> Image:
    downloaded_file = await bot.download(file_id)
    return Image.open(downloaded_file)


def dominant_color(image: Image) -> tuple[float]:
    width, height = 150, 150
    image = image.resize((width, height), resample=0)
    pixels = image.getcolors(width * height)
    sorted_pixels = sorted(pixels, key=lambda p: p[0])
    return sorted_pixels[-1][1]
