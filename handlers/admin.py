import asyncio
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import load_data

ADMIN_ID = 7166220534

class MassMessageForm(StatesGroup):
    text = State()
    inline_button = State()

mass_router = Router()

@mass_router.message(Command("rassil"))
async def start_mass_message(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав для использования этой команды.")
        return

    await message.answer("Введите текст для рассылки:")
    await state.set_state(MassMessageForm.text)


@mass_router.message(MassMessageForm.text)
async def process_mass_message_text(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not text:
        await message.answer("Текст не может быть пустым.")
        return

    await state.update_data(text=text)
    await message.answer("Введите текст инлайн-кнопки или 'None', если кнопка не нужна:")
    await state.set_state(MassMessageForm.inline_button)


@mass_router.message(MassMessageForm.inline_button)
async def process_inline_button(message: types.Message, state: FSMContext):
    button_text = message.text.strip()
    data = await state.get_data()
    text = data['text']

    if button_text.lower() == 'none':
        markup = None
    else:
        markup = InlineKeyboardBuilder()
        markup.add((InlineKeyboardButton(text=button_text, url='http://t.me/+CBzwjL3a4CU4NzQy')))

    data = load_data()
    users = data['users']
    print(users)

    sent_count = 0
    failed_count = 0

    for user_id in users:
        try:
            await message.bot.send_message(user_id, text, reply_markup=markup.as_markup())
            sent_count += 1
        except Exception as e:
            failed_count += 1

    await message.answer(f"Рассылка завершена.\nОтправлено: {sent_count}\nНе отправлено: {failed_count}")
    await state.clear()

