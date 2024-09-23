import asyncio
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.banned import unban_user, ban_user
from database.db import load_data, load_data_mail
from kb import admin_panel

ADMINS_ID = [6184515646, 7166220534]

class MassMessageForm(StatesGroup):
    text = State()
    inline_button = State()
    mails = State()
    ban_user = State()
    unban_user = State()

mass_router = Router()

@mass_router.message(Command("admin"))
async def start_mass_message(message: types.Message):
    if message.from_user.id not in ADMINS_ID:
        await message.answer("У вас нет прав для использования этой команды.")
        return

    await message.answer("Привет админ!", reply_markup=await admin_panel())

@mass_router.callback_query(lambda call: call.data == 'mails')
async def mailing_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите user_id пользователя для просмотра почт:")
    await state.set_state(MassMessageForm.mails)

@mass_router.callback_query(lambda call: call.data == 'mailing')
async def mailing_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите текст для рассылки:")не дое
    await state.set_state(MassMessageForm.text)


@mass_router.callback_query(lambda call: call.data == 'ban')
async def ban_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите user_id для бана:")
    await state.set_state(MassMessageForm.ban_user)


@mass_router.callback_query(lambda call: call.data == 'unban')
async def unban_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите user_id для разбана:")
    await state.set_state(MassMessageForm.unban_user)

@mass_router.message(MassMessageForm.mails)
async def mails_get(message: types.Message, state: FSMContext):
    user_id = message.text.strip()

    data = load_data_mail()

    user_data = data.get("users", {}).get(user_id)

    if user_data and "emails" in user_data:
        emails = user_data["emails"]
        if emails:
            email_list = "\n".join(emails)
            await message.answer(f"Почты для пользователя {user_id}:\n{email_list}")
        else:
            await message.answer(f"У пользователя {user_id} нет почт.")
    else:
        await message.answer(f"Пользователь с ID {user_id} не найден.")

    await state.clear()


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


@mass_router.message(MassMessageForm.ban_user)
async def process_ban_user(message: types.Message, state: FSMContext):
    user_id = message.text.strip()

    ban_user(user_id)
    await message.answer(f"Пользователь {user_id} забанен.")

    await state.clear()


@mass_router.message(MassMessageForm.unban_user)
async def process_unban_user(message: types.Message, state: FSMContext):
    user_id = message.text.strip()

    unban_user(user_id)
    await message.answer(f"Пользователь {user_id} разбанен.")
    await state.clear()
