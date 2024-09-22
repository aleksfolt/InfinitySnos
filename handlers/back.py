from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery
from database.db import load_data, save_data
from kb import start_kb
from states import proxy_count

back_router = Router()

@back_router.callback_query(F.data == "back")
async def back_to_menu(callback: CallbackQuery):

    data = load_data()
    if callback.from_user.id not in data["users"]:
        data["users"].append(callback.from_user.id)
        save_data(data)
    await callback.bot.edit_message_text(text=f"Добро пожаловать.\n"
                          f"- пользователей: {len(data['users'])}\n"
                          f"- прокси: {proxy_count}\n"
                          f"- версия бота: 0.3",
                                         chat_id=callback.message.chat.id,
                                         message_id=callback.message.message_id,
                                         reply_markup=await start_kb(callback), parse_mode=ParseMode.MARKDOWN
                          )