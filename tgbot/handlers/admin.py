import asyncio
import os.path

from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, InputFile, Message
from aiogram.utils import exceptions

from db_py.db import Database
from tgbot.config import load_config
from tgbot.keyboards.inline import admin_keyboard
from tgbot.states.states import Mailing

db = Database()
config = load_config(".env.dist")

async def admin(message: Message):
    await message.answer(text="Панель админа", reply_markup=admin_keyboard)


async def send_message(user_id: int, text: str, disable_notification: bool = False) -> bool:
    bot = Bot.get_current()
    await bot.send_message(user_id, text, disable_notification=disable_notification)
    

async def mailing(message: Message, state: FSMContext):
    await state.finish()
    users = db.select_all_users()
    await message.answer("Рассылка начата")
    for user in users:
            if await send_message(user[0], message.text):
                count += 1
            await asyncio.sleep(.08)
    await message.answer("Рассылка завершена")


async def ban(message: Message):
    args = message.get_args()
    
    try:
        user_id = int(args)
    except:
        await message.reply("Не верно введен id")
        return
    is_ban = 1
    sql = "UPDATE Users SET is_ban=? WHERE user_id=?"
    db.execute(sql, (is_ban, user_id), commit=True)


async def unban(message: Message):
    args = message.get_args()
    try:
        user_id = int(args)
    except:
        await message.reply("Не верно введен id")
        return
    is_ban = 0
    sql = "UPDATE Users SET is_ban=? WHERE user_id=?"
    db.execute(sql, (is_ban, user_id), commit=True)


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin, commands=["admin"], state="*", is_admin=True)
    dp.register_message_handler(ban, commands=["ban"], state="*", is_admin=True)
    dp.register_message_handler(unban, commands=["unban"], state="*", is_admin=True)
    dp.register_message_handler(mailing, is_admin=True, state=Mailing.mailing_message)
