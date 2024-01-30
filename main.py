import telebot
from telebot import types
from flask import Flask, request, send_from_directory, send_file, jsonify, render_template, url_for
from petpetgif.saveGif import save_transparent_gif
from io import BytesIO, StringIO
from PIL import Image,ImageDraw,ImageFont, ImageStat
import textwrap
from pkg_resources import resource_stream
from threading import Thread
from googleapiclient import discovery
import time
import schedule
import requests
from bs4 import BeautifulSoup
import random
import re
import os
import json
import html
import math
from sqlalchemy import create_engine
import traceback
from datetime import datetime, timedelta

KIRYA = 630112565
API_KEY = 'AIzaSyBhxiNkKtphrX4TwPU-cOFIKY6v7q_GIFM'

token = '6639737408:AAHOfnimdR2Gp0_mOS65k1i-Qm2YV_Co564'
class ExHandler(telebot.ExceptionHandler):
    def handle(self, exc):
        bot.send_message(738931917, traceback.format_exc())
        return True
bot = telebot.TeleBot(token, threaded=True, num_threads=10, parse_mode='HTML', exception_handler = ExHandler())

APP_URL = f'https://fknbot.onrender.com/{token}'
app = Flask(__name__)
bot.remove_webhook()
bot.set_webhook(url=APP_URL, allowed_updates=['message',  'callback_query', 'chat_member'])

username = os.environ['USERNAME']
password = os.environ['PASSWORD']
cursor = create_engine(f'mysql+pymysql://{username}:{password}@eu-central.connect.psdb.cloud:3306/nekodb', pool_recycle=280, connect_args={'ssl': {'ssl-mode': 'preferred'}})
db = []
# ☣️

def get_toxicity_level(user_id):
    data = cursor.execute(f"SELECT level FROM users WHERE id = {user_id}")
    data = data.fetchone()
    if data is None:
        level = 0
    else:
        level = data[0]
    return level

def dominant_color(image):
    width, height = 150,150
    image = image.resize((width, height),resample = 0)
    #Get colors from image object
    pixels = image.getcolors(width * height)
    #Sort them by count number(first element of tuple)
    sorted_pixels = sorted(pixels, key=lambda t: t[0])
    #Get the most frequent color
    dominant_color = sorted_pixels[-1][1]
    return dominant_color
 
def make(source, clr):
    frames = 10
    resolution = (256, 256)
    delay = 20
    images = []
    base = source.convert('RGBA').resize(resolution)

    for i in range(frames):
        squeeze = i if i < frames/2 else frames - i
        width = 0.8 + squeeze * 0.02
        height = 0.8 - squeeze * 0.05
        offsetX = (1 - width) * 0.5 + 0.1
        offsetY = (1 - height) - 0.08

        canvas = Image.new('RGBA', size=resolution, color=clr)
        canvas.paste(base.resize((round(width * resolution[0]), round(height * resolution[1]))), (round(offsetX * resolution[0]), round(offsetY * resolution[1])))
        with Image.open(resource_stream(__name__, f"pet/pet{i}.gif")).convert('RGBA').resize(resolution) as pet:
            canvas.paste(pet, mask=pet)
        images.append(canvas)
    bio = BytesIO()
    bio.name = 'result.gif'
    save_transparent_gif(images, durations=20, save_file=bio)
    bio.seek(0)
    return bio

def to_fixed(f: float, n=0):
    a, b = str(f).split('.')
    return '{}.{}{}'.format(a, b[:n], '0'*(n-len(b)))

def set_reaction(chat,message,reaction,big = False):
    react = json.dumps([{
        "type": "emoji",
        "emoji": reaction
    }])
    dat = {
        "chat_id": chat,
        "message_id": message,
        "reaction": react,
        "is_big": big
    }
    with requests.Session() as s:
        link = f"https://api.telegram.org/bot{token}/setMessageReaction"
        p = s.post(link, data=dat)
        print(p.json())

def del_reaction(chat,message):
    dat = {
        "chat_id": chat,
        "message_id": message,
    }
    with requests.Session() as s:
        link = f"https://api.telegram.org/bot{token}/setMessageReaction"
        p = s.post(link, data=dat)
        print(p.json())

def get_pil(fid):
    file_info = bot.get_file(fid)
    downloaded_file = bot.download_file(file_info.file_path)
    im = Image.open(BytesIO(downloaded_file))
    return im

def send_pil(im):
    bio = BytesIO()
    bio.name = 'result.png'
    im.save(bio, 'PNG')
    bio.seek(0)
    return bio

def analize_toxicity(text):
    client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=API_KEY,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        static_discovery=False,
    )
    analyze_request = {
        'comment': { 'text': text },
        'requestedAttributes': {'TOXICITY': {}},
        'languages': ['ru']
    }
    response = client.comments().analyze(body=analyze_request).execute()
    return response['attributeScores']['TOXICITY']['summaryScore']['value']

def draw_text_rectangle(draw,text,rect_w,rect_h,cord_x,cord_y):
    text = text.upper()
    lines = textwrap.wrap(text, width=16)
    text = '\n'.join(lines)
    selected_size = 1
    for size in range(1, 150):
        arial = ImageFont.FreeTypeFont('comicbd.ttf', size=size)
        #w, h = arial.getsize(text)
        w, h = draw.multiline_textsize(text=text,font=arial,spacing=0)
        if w > rect_w or h > rect_h:
            break 
        selected_size = size   
    arial = ImageFont.FreeTypeFont('comicbd.ttf', size=selected_size)
    draw.multiline_text((cord_x, cord_y), text, fill='black', anchor='mm', font=arial, align='center', spacing=0)

@bot.message_handler(commands=["necoarc"])
def msg_necoarc(message):
        if message.reply_to_message is None or (message.reply_to_message.text is None and message.reply_to_message.caption is None):
            bot.send_message(message.chat.id, 'Ответом на текст еблан',reply_to_message_id=message.message_id)
            return
        with Image.open('necoarc.png') as img:
            draw = ImageDraw.Draw(img)
            if message.reply_to_message.text is not None:
                text = message.reply_to_message.text
            else:
                text = message.reply_to_message.caption
            draw_text_rectangle(draw, text, 220, 106, 336, 80)
            bot.add_sticker_to_set(user_id=738931917,name='necoarc_by_fknclown_bot',emojis='🫵',png_sticker=send_pil(img))
            sset = bot.get_sticker_set('necoarc_by_fknclown_bot')
            bot.send_sticker(message.chat.id, sset.stickers[-1].file_id)

@bot.message_handler(commands=["pet"])
def msg_pet(message):
        if message.reply_to_message is None:
            bot.send_message(message.chat.id, 'Ответом на сообщение еблан',reply_to_message_id=message.message_id)
            return
        r = bot.get_user_profile_photos(message.reply_to_message.from_user.id)
        if len(r.photos) == 0:
            bot.send_message(message.chat.id, 'У этого пидора нет авы',reply_to_message_id=message.message_id)
            return
        fid = r.photos[0][-1].file_id
        img = get_pil(fid)
        mean = dominant_color(img)
        f = make(img, mean)
        bot.send_animation(message.chat.id,f,reply_to_message_id=message.reply_to_message.message_id) 

@bot.message_handler(commands=["cube"])
def msg_cube(message):
        print('принято')
        if message.reply_to_message is None:
            bot.send_message(message.chat.id, 'Ответом на сообщение еблан',reply_to_message_id=message.message_id)
            return
        r = bot.get_user_profile_photos(message.reply_to_message.from_user.id)
        if len(r.photos) == 0:
            bot.send_message(message.chat.id, 'У этого пидора нет авы',reply_to_message_id=message.message_id)
            return
        fid = r.photos[0][-1].file_id
        file_info = bot.get_file(fid)
        downloaded_file = bot.download_file(file_info.file_path)
        bio = BytesIO(downloaded_file)
        bio.name = 'result.png'
        bio.seek(0)
        direct = random.choice(['left','right'])
        dat = {
            "target": (None,1),
            "MAX_FILE_SIZE": (None,1073741824),
            "image[]": ('result.png',bio.getvalue()),
            "speed": (None,"ufast"),
            "bg_color": (None,"000000"),
            "direction": (None,direct)
        }
        with requests.Session() as s:
            p = s.get("https://en.bloggif.com/cube-3d")
            soup = BeautifulSoup(p.text, 'lxml')
            tkn = soup.find('form')
            linkfrm = "https://en.bloggif.com" + tkn['action']
            p = s.post(linkfrm, files=dat)
            print(p)
            soup = BeautifulSoup(p.text, 'lxml')
            img = soup.find('a', class_='button gray-button')
            linkgif = "https://en.bloggif.com" + img['href']
            p = s.get(linkgif)
            bio = BytesIO(p.content)
            bio.name = 'result.gif'
            bio.seek(0)
            bot.send_animation(message.chat.id,bio,reply_to_message_id=message.reply_to_message.message_id)

@bot.message_handler(commands=["paint"])
def msg_paint(message):
            markup = telebot.types.InlineKeyboardMarkup()
            button1 = telebot.types.InlineKeyboardButton("Рисовать 🎨", url=f'https://t.me/fknclown_bot/paint?startapp={message.chat.id}')
            markup.add(button1)
            bot.send_message(message.chat.id,'Нажми на кнопку чтобы отправить свой клоунский рисунок', reply_markup=markup)

@bot.message_handler(commands=["set"])
def msg_set(message):
    if message.from_user.id != 738931917:
        bot.send_message(message.chat.id, 'Угомонись хохлинка',reply_to_message_id=message.message_id)
        return
    arg = int(message.text.split()[1])
    chel = html.escape(message.reply_to_message.from_user.first_name, quote = True)
    data = cursor.execute(f"SELECT id FROM users WHERE id = {message.reply_to_message.from_user.id}")
    data = data.fetchone()
    if data is None:
        cursor.execute(f"INSERT INTO users (id, name, level) VALUES ({message.reply_to_message.from_user.id}, %s, {arg})", chel)
    else:
        cursor.execute(f"UPDATE users SET level = {arg}, name = %s WHERE id = {message.reply_to_message.from_user.id}", chel)

@bot.message_handler(commands=["toxic"])
def msg_toxic(message):
    if message.reply_to_message is None or message.reply_to_message.from_user.id < 0:
        bot.send_message(message.chat.id, 'Ответом на сообщение еблан',reply_to_message_id=message.message_id)
        return
    level = get_toxicity_level(message.reply_to_message.from_user.id)
    text = f'Уровень токсичности:  {level} ☣️\n'
    if level < 10:
        leveltext = 'Добрый чел позитивный'
    elif level < 40:
        leveltext = 'Норм чел'
    elif level < 100:
        leveltext = 'С гнильцой человек'
    elif level < 200:
        leveltext = 'Неадекват ебаный'
    elif level < 400:
        leveltext = 'Опасен для общества, изолируйте нахуй'
    elif level < 1000:
        leveltext = 'Угроза для страны, данные переданы в СБУ'
    elif level < 2000:
        leveltext = 'Подлежит устранению согласно решению собвеза ООН'
    else:
        leveltext = '[ДАННЫЕ УДАЛЕНЫ]'
        
    text += f'Диагноз:  {leveltext}'
    bot.send_message(message.chat.id,text,reply_to_message_id=message.reply_to_message.message_id)

@bot.message_handler(commands=["top"])
def msg_top(message):
    text = 'Эти челы написали больше всего токсичных сообщений. Могут ли они гордиться этим? Несомненно\n\n'
    data = cursor.execute(f'SELECT id, name, level FROM users ORDER BY level DESC LIMIT 10')
    data = data.fetchall()
    i = 1
    if data is not None:
        for d in data:
            idk = d[0]
            name = d[1]
            level = d[2]
            if i == 1:
                text += f'🏆 <b>{name}</b>  {level} ☣️\n'
            else:
                text += f'{i}.  {name}  {level} ☣️\n'
            i += 1
    bot.send_message(message.chat.id,text,reply_to_message_id=message.message_id) 

def handle_text(message, txt):
        print('Сообщение получено')
        if message.chat.id < 0 and message.chat.id not in db:
            db.append(message.chat.id)
            cursor.execute(f'INSERT INTO chats (id) VALUES ({message.chat.id})')
        #res = text2toxicity(txt, False)
        if message.from_user.id == KIRYA:
            return
        res = analize_toxicity(txt)
        if (res > 0.6) and (message.from_user.id > 0):
            chel = html.escape(message.from_user.first_name, quote = True)
            set_reaction(message.chat.id,message.id,"😈")
            if message.chat.id in [-1001694727085, -1001646530790, -1001596293991, -1001592397575, -1001152773192]:
                data = cursor.execute(f"SELECT id FROM users WHERE id = {message.from_user.id}")
                data = data.fetchone()
                if data is None:
                    cursor.execute(f"INSERT INTO users (id, name) VALUES ({message.from_user.id}, %s)", chel)
                else:
                    cursor.execute(f"UPDATE users SET level = level + 1, name = %s WHERE id = {message.from_user.id}", chel)
        text_for_reaction = re.sub('[^а-я]', ' ', txt.lower()).split()
        if 'сбу' in text_for_reaction:
            print('сбу')
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEKWrBlDPH3Ok1hxuoEndURzstMhckAAWYAAm8sAAIZOLlLPx0MDd1u460wBA',reply_to_message_id=message.message_id)
        elif 'порох' in text_for_reaction or 'порошенко' in text_for_reaction or 'гетьман' in text_for_reaction or 'рошен' in text_for_reaction:
            print('порох')
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEK-splffs7OZYtr8wzINEw4lxbvwywoAACXSoAAg2JiEoB98dw3NQ3FjME',reply_to_message_id=message.message_id)
        elif 'зелебоба' in text_for_reaction or 'зелень' in text_for_reaction or 'зеленский' in text_for_reaction or 'зеленський' in text_for_reaction:
            print('зелебоба')
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELGOplmDc9SkF-ZnVsdNl4vhvzZEo7BQAC5SwAAkrDgEr_AVwN_RkClDQE',reply_to_message_id=message.message_id)

@bot.message_handler(func=lambda message: True, content_types=['photo','video','document','text','animation'])
def msg_text(message):
    if message.chat.id == -1001694727085 and message.photo is not None:
        bot.send_message(message.chat.id,str(message.photo[-1].file_id) + ' ' + str(message.photo[-1].file_size) + ' ' + bot.get_file_url(message.photo[-1].file_id), reply_to_message_id=message.message_id)
    if message.chat.id == -1001694727085 and message.animation is not None:
        bot.send_message(message.chat.id,str(message.animation.file_id), reply_to_message_id=message.message_id)
    if message.text is not None:
        handle_text(message, message.text)
    elif message.caption is not None:
        handle_text(message, message.caption)

@bot.chat_member_handler()
def msg_chat(upd):
    print(upd.new_chat_member)
    if upd.new_chat_member.status == "kicked":
        chel = html.escape(upd.new_chat_member.user.first_name, quote = True)
        bot.send_message(upd.chat.id, chel)
        bot.send_animation(upd.chat.id, 'CgACAgIAAx0CZQN7rQABAvvXZYaTUqw6yY1aRLQS4-ne8Xg4nmkAAociAAKNM5BKbkRUYQABc69sMwQ')
    elif upd.new_chat_member.status == "left" and upd.old_chat_member.status != "kicked":
        chel = html.escape(upd.new_chat_member.user.first_name, quote = True)
        bot.send_message(upd.chat.id, chel)
        bot.send_animation(upd.chat.id, 'CgACAgIAAx0CZQN7rQABAv8oZYhghoptaY54elnBAm0-wjRmcxoAAhkoAAJpwchJ_S12XgABifSrMwQ')

@app.route('/' + token, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'ok', 200
    
@app.route('/')
def get_ok():
    return 'ok', 200

@app.route('/send_paint/<chatid>', methods=['POST'])
def send_paint(chatid):
        file = request.files.get("file")
        bio = BytesIO()
        bio.name = 'result.png'
        file.save(bio)
        bio.seek(0)
        bot.send_photo(int(chatid),photo = bio)
        #-1001152773192
        return '!', 200

@app.route('/paint')
def get_paint():
        return render_template("paint.html")

def updater():
    print('Поток запущен')
    while True:
        schedule.run_pending()
        time.sleep(1)
        
def jobday():
    for chatid in db:
        try:
            bot.send_sticker(chatid, 'CAACAgIAAxkBAAEKWq5lDOyAX1vNodaWsT5amK0vGQe_ggACHCkAAspLuUtESxXfKFwfWTAE')
        except Exception as e:
            print(e)

def init_db():
    data = cursor.execute('SELECT id FROM chats')
    data = data.fetchall()
    if data is not None:
        for dat in data:
            db.append(dat[0])
    print(db)

if __name__ == '__main__':
    init_db()
    bot.send_message(738931917, 'Запущено')
    schedule.every().day.at("23:00").do(jobday)
    t = Thread(target=updater)
    t.start()
    app.run(host='0.0.0.0',port=80, threaded = True)