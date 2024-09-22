import random

from aiogram.fsm.state import StatesGroup, State

proxy_count = random.randint(3000, 5000)
active_sending = {}

class Form(StatesGroup):
    text_to_send = State()
    bot_net_to_send = State()
    email_input = State()
    link_to_report = State()
    custom_report_text = State()
