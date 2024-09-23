from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types, F, Router
from aiogram.types import Message


async def start_kb(user_id):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="r3port", callback_data=f"report"))
    builder.row(types.InlineKeyboardButton(text="История", callback_data=f"history"))
    builder.row(types.InlineKeyboardButton(text="bot-net", callback_data=f"bot_net"))
    builder.row(types.InlineKeyboardButton(text="mail", callback_data=f"mail"))
    return builder.as_markup()



async def get_back_button():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))
    return keyboard.as_markup()

async def get_post_send_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text="История", callback_data="history"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))
    return keyboard.as_markup()


async def admin_panel():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Рассылка", callback_data="mailing"))
    builder.add(types.InlineKeyboardButton(text="Почты", callback_data="mails"))
    builder.add(types.InlineKeyboardButton(text="Бан", callback_data="ban"))
    builder.add(types.InlineKeyboardButton(text="Разбан", callback_data="unban"))
    builder.adjust(2, 2)
    return builder.as_markup()
