import asyncio

from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from states import Form
from kb import get_back_button, get_post_send_keyboard

bot_net_router = Router()


@bot_net_router.callback_query(lambda call: call.data == "bot_net")
async def bot_net_menu(call: types.CallbackQuery):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text="Спам/Насилие", callback_data='reason_spam'))
    keyboard.row(types.InlineKeyboardButton(text="Детская порнография", callback_data='reason_child_porn'))
    keyboard.row(types.InlineKeyboardButton(text="Наркотики/Личные данные", callback_data='reason_drugs'))
    keyboard.row(types.InlineKeyboardButton(text="Назад", callback_data='back'))

    await call.message.edit_text("Выберите причину:", reply_markup=keyboard.as_markup())


@bot_net_router.callback_query(lambda call: call.data.startswith('reason_'))
async def process_bot_net_reason(call: types.CallbackQuery, state: FSMContext):
    back_button = InlineKeyboardBuilder()
    back_button.add(types.InlineKeyboardButton(text="Назад", callback_data='back'))

    await call.message.edit_text("📨 Введите ссылку на нарушение:", reply_markup=back_button.as_markup())
    await state.set_state(Form.bot_net_to_send)


@bot_net_router.message(Form.bot_net_to_send)
async def process_text_to_send(message: types.Message, state: FSMContext):
    text = message.text
    user_id = message.chat.id
    await state.clear()
    await simulate_sending_bot(message.bot, text, user_id)


async def simulate_sending_bot(bot, text: str, user_id: int):
    msg = await bot.send_message(user_id, f"Запущен процесс Bot-Net\nОтправлено: 0/28\nМетод: Session")

    for i in range(1, 29):
        await asyncio.sleep(1)
        await bot.edit_message_text(f"Запущен процесс Bot-Net\nОтправлено: {i}/28\nМетод: Session",
                                    chat_id=msg.chat.id, message_id=msg.message_id)

    await bot.send_message(user_id, "Сообщение отправлено.", reply_markup=await get_post_send_keyboard())
