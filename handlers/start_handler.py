from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, InputFile, FSInputFile

from database.db import load_data, save_data
from kb import start_kb
from states import proxy_count

start_router = Router()

@start_router.message(Command("start"))
async def start_handler(msg: Message):
    data = load_data()
    if msg.from_user.id not in data["users"]:
        data["users"].append(msg.from_user.id)
        save_data(data)
    photo = FSInputFile("assets/img.png")
    """await msg.bot.send_photo(
        chat_id=msg.chat.id,
        photo=photo,
        caption=f"Добро пожаловать.\n"
                f"- пользователей: {len(data['users'])}\n"
                f"- прокси: {proxy_count}\n"
                f"- версия бота: 0.3\n\n"
                f"Разработчик: @folted",
        reply_markup=await start_kb(msg),
        parse_mode=ParseMode.MARKDOWN
    )"""

    await msg.answer(text=f"Добро пожаловать.\n"
                          f"- пользователей: {len(data['users'])}\n"
                          f"- прокси: {proxy_count}\n"
                          f"- версия бота: 0.3\n\n"
                          f"Разработчик: @folted",
                     reply_markup=await start_kb(msg), parse_mode=ParseMode.MARKDOWN)
