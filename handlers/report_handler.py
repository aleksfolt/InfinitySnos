import asyncio
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import load_data, save_data
from kb import get_back_button, get_post_send_keyboard
from states import Form, active_sending

report_router = Router()


@report_router.callback_query(lambda call: call.data == "report")
async def process_report(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.message.chat.id
    if active_sending.get(user_id):
        await callback.answer("У вас уже запущен процесс отправки.")
        return

    back_button = InlineKeyboardBuilder()
    back_button.add(types.InlineKeyboardButton(text="Назад", callback_data='back'))

    await callback.message.edit_text("📨 Введите свой текст для отправки:",
                                     reply_markup=back_button.as_markup())

    await state.set_state(Form.text_to_send)


@report_router.message(Form.text_to_send)
async def process_text_to_send(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    text = message.text

    active_sending[user_id] = True

    msg = await message.answer(f"Текст:\n{text}\nОтправлено: 0/30", reply_markup=await get_back_button())
    await state.clear()
    await simulate_sending(message.bot, msg, text, user_id)


async def simulate_sending(bot, msg: types.Message, text: str, user_id: int):
    try:
        data = load_data()
        data['history'].append({"user": msg.chat.id, "text": text})
        save_data(data)

        for i in range(1, 31):
            await asyncio.sleep(1)
            await bot.edit_message_text(f"Текст:\n{text}\nОтправлено: {i}/30",
                                        chat_id=msg.chat.id, message_id=msg.message_id,
                                        reply_markup=await get_back_button())
        await bot.send_message(msg.chat.id, "Сообщение отправлено.", reply_markup=await get_post_send_keyboard())
    finally:
        active_sending[user_id] = False
