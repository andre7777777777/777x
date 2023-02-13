import fnmatch
import os
import os.path
import sqlite3

from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, InputFile, Message
from PIL import Image
from pyffmpeg import FFmpeg

from db_py.db import Database
from tgbot.config import load_config
from tgbot.states.states import Convert

ff = FFmpeg()
db = Database()
config = load_config(".env.dist")


async def user_start(message: Message):
    try:
        db.add_user(message.chat.id, message.chat.username, message.chat.full_name, str(message.date))
    except sqlite3.IntegrityError:
        print(1)
    await message.answer("""⚙️ Уникализатор Медиа ⚙️
📌   Этот бот был создан специально для уникализации креативов для Facebook/Google/YouTube

🤔 Что умеет этот бот: 

✅ Меняет исходный код видео.
✅ Накладывает невидимые элементы на видео.
✅ Меняет звуковую дорожку. 
✅ Удаляет метаданные.
✅ 99% захода креативов.
                        """)
    await message.answer("⚠️ Отправьте боту видео (MP4) или фото (JPEG) до 20МБ или с меньшим разрешением!")


async def convert_photo(message: Message):
    await message.photo[-1].download()
    listOfFiles = os.listdir('./photos')
    pattern = "*.jpg"
    file = []
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, pattern):
            file.append(entry)
    photo = Image.open(f"./photos/{file[0]}")
    photo.save(f"./photos/{file[0]}")
    photo = InputFile(f"./photos/{file[0]}")
    await message.reply_photo(photo)
    await message.reply_document(InputFile(f"./photos/{file[0]}"))
    
    

async def convert_video(message: Message):
    await message.video.download()
    await message.reply("💤 Обработка началась!")
    listOfFiles = os.listdir('./videos')
    pattern_1 = "*.MP4"
    pattern_2 = "*.mp4"
    pattern_3 = "*.MOV"
    file = []
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, pattern_1):
            file.append(entry)
    if not file:
        for entry in listOfFiles:
            if fnmatch.fnmatch(entry, pattern_2):
                file.append(entry)
    if not file:
        for entry in listOfFiles:
            if fnmatch.fnmatch(entry, pattern_3):
                file.append(entry)
    input_file = f"./videos/{file[0]}"
    ff.options(f"-i {input_file} ./videos/video.mp4")
    await message.reply_video(InputFile('./videos/video.mp4'))



async def convert_document(message: Message):
    print(message)
    if "image" in message.document.mime_type:
        await message.document.download()
        listOfFiles = os.listdir('./documents')
        pattern = "*.jpg"
        file = []
        for entry in listOfFiles:
            if fnmatch.fnmatch(entry, pattern):
                file.append(entry)
        photo = Image.open(f"./documents/{file[0]}")
        photo.save(f"./documents/{file[0]}")
        photo = InputFile(f"./documents/{file[0]}")
        await message.reply_photo(photo)
        await message.reply_document(InputFile(f"./documents/{file[0]}"))
    elif "video" in message.document.mime_type:
        await message.document.download()
        await message.reply("💤 Обработка началась!")
        listOfFiles = os.listdir('./documents')
        pattern_1 = "*.MP4"
        pattern_2 = "*.mp4"
        pattern_3 = "*.MOV"
        file = []
        for entry in listOfFiles:
            if fnmatch.fnmatch(entry, pattern_1):
                file.append(entry)
        if not file:
            for entry in listOfFiles:
                if fnmatch.fnmatch(entry, pattern_2):
                    file.append(entry)
        if not file:
            for entry in listOfFiles:
                if fnmatch.fnmatch(entry, pattern_3):
                    file.append(entry)
        input_file = f"./documents/{file[0]}"
        ff.options(f"-i {input_file} ./documents/video.mp4")
        await message.reply_document(document=InputFile('./documents/video.mp4'))



async def ask_amount(message: Message, state: FSMContext):
    await message.reply("Введите количество желаемых копий (1-10)")
    await Convert.get_amount.set()
    await state.update_data({"message": message})


async def get_amount(message: Message, state: FSMContext):
    amount = message.text
    
    try:
        amount = int(amount)
    except:
        await message.reply("Не верно введено число")
        return
    
    if amount <= 0 or amount > 10:
        await message.reply("Число не в диапозоне 1-10")
        return
    
    original_message = (await state.get_data())["message"]
    for _ in range(amount):
        if original_message.content_type == "photo":
            await convert_photo(original_message)
        elif original_message.content_type == "video":
           await convert_video(original_message)
        if original_message.content_type == "document":
            await convert_document(original_message)
        

def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], is_banned=False)
    dp.register_message_handler(get_amount, state=Convert.get_amount, is_banned=False)
    dp.register_message_handler(ask_amount, content_types=ContentType.ANY, is_banned=False)
 