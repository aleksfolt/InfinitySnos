from aiogram import types, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import load_data
from aiogram.fsm.context import FSMContext
from kb import get_back_button

history_router = Router()

@history_router.callback_query(lambda call: call.data == 'history')
async def show_history(call: types.CallbackQuery, state: FSMContext):
    await display_history(call, 0)

async def display_history(call: types.CallbackQuery, page: int):
    user_id = call.message.chat.id
    data = load_data()
    history = [entry for entry in data['history'] if entry['user'] == user_id]

    if not history:
        await call.message.edit_text(text="История пуста.")
        return

    per_page = 5
    start = page * per_page
    end = start + per_page

    history_page = history[start:end]
    history_text = "\n\n".join([f"Текст: {entry.get('text', 'Нет данных')}" for entry in history_page])

    navigation_buttons = InlineKeyboardBuilder()
    if page > 0:
        navigation_buttons.add(types.InlineKeyboardButton(text="Назад", callback_data=f'history_page_{page - 1}'))
    if end < len(history):
        navigation_buttons.add(types.InlineKeyboardButton(text="Вперед", callback_data=f'history_page_{page + 1}'))
    navigation_buttons.add(types.InlineKeyboardButton(text="Главное меню", callback_data='back'))

    await call.message.edit_text(
        text=f"История (страница {page + 1}):\n\n{history_text}",
        reply_markup=navigation_buttons.as_markup()
    )

@history_router.callback_query(lambda call: call.data.startswith('history_page_'))
async def paginate_history(call: types.CallbackQuery):
    page = int(call.data.split('_')[-1])
    await display_history(call, page)
