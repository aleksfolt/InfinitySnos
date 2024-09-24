import asyncio
import random
import string
import aiohttp
from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.db import load_data, save_data
from kb import get_back_button, get_post_send_keyboard
from states import Form, active_sending

report_router = Router()


async def generate_email(domain="gmail.com"):
    username_length = random.randint(5, 10)
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=username_length))
    return f"{username}@{domain}"


async def generate_phone():
    country_code = "+7"
    phone_number = ''.join(random.choices(string.digits, k=10))
    return f"{country_code} {phone_number}"


async def send_request(text):
    url = 'https://telegram.org/support'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': 'stel_ssid=6b9e2c7d956a7bc273_14923606160579152165',
        'origin': 'https://telegram.org',
        'priority': 'u=0, i',
        'referer': 'https://telegram.org/support',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Brave";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }

    data = {
        'message': text,
        'email': await generate_email(),
        'phone': await generate_phone(),
        'setln': ''
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            text = await response.text()
            status_code = response.status
            return status_code


@report_router.callback_query(lambda call: call.data == "report")
async def process_report(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.message.chat.id
    if active_sending.get(user_id):
        await callback.answer("⚠️ У вас уже запущен процесс отправки.")
        return

    back_button = InlineKeyboardBuilder()
    back_button.add(types.InlineKeyboardButton(text="⏪ Назад", callback_data='back'))

    await callback.message.edit_text("💻 Введите свой текст для отправки:",
                                     reply_markup=back_button.as_markup())

    await state.set_state(Form.text_to_send)


@report_router.message(Form.text_to_send)
async def process_text_to_send(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    text = message.text

    num = random.uniform(0.7, 1.5)
    msg = await message.answer("<blockquote> 🔄 Try to connect... </blockquote>", parse_mode=ParseMode.HTML)
    code = await send_request(text)
    if code == 200:
        status = "Успешно ✅"
    else:
        status = f"Произошла ошибка ⚠️. Код: {code}"
    await asyncio.sleep(num)
    await msg.edit_text(f"💬 Текст: <blockquote>{text} </blockquote>\n<blockquote>🕓 Время отправки: {message.date} </blockquote>\n<blockquote>❗️ Статус: {status} </blockquote>",
                               reply_markup=await get_back_button(),
                               parse_mode=ParseMode.HTML,
                                        )
    await state.clear()


async def simulate_sending(bot, msg: types.Message, text: str, user_id: int):
    try:
        data = load_data()
        data['history'].append({"user": msg.chat.id, "text": text})
        save_data(data)

        for i in range(1, 31):
            await asyncio.sleep(1)
            await bot.edit_message_text(f"💻 Сообщение:\n`{text}`\n📡 Отправлено: {i}/30 пакетов",
                                        chat_id=msg.chat.id, message_id=msg.message_id,
                                        reply_markup=await get_back_button())
        await bot.send_message(msg.chat.id, "🖥️ **Отправка завершена. Миссия выполнена**.",
                               reply_markup=await get_post_send_keyboard())
    finally:
        active_sending[user_id] = False
