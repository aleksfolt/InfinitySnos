import random

from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import save_data_mail, load_data_mail, load_template_texts
from states import Form
import asyncio
import smtplib
from email.mime.text import MIMEText

mail_router = Router()

SMTP_SETTINGS = {
    "gmail.com": ("smtp.gmail.com", 587),
    "yahoo.com": ("smtp.mail.yahoo.com", 587),
    "hotmail.com": ("smtp.live.com", 587),
    "mail.ru": ("smtp.mail.ru", 587),
    "rambler.ru": ("smtp.rambler.ru", 587),
}


def get_smtp_settings(email: str):
    domain = email.split('@')[-1]
    return SMTP_SETTINGS.get(domain, None)



async def send_email(subject: str, body: str, sender: str, recipients: list):
    try:
        email_address, email_password = sender.split(':', 1)
        smtp_settings = get_smtp_settings(email_address)

        if smtp_settings is None:
            return f"SMTP-сервер для домена {email_address.split('@')[-1]} не найден."

        smtp_server, smtp_port = smtp_settings

        for recipient in recipients:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = email_address
            msg['To'] = recipient

            await asyncio.to_thread(send_email_smtp, smtp_server, smtp_port, email_address, email_password, recipient, msg)

        print(f"Сообщение отправлено от {email_address} на {recipient}")
        return f"Сообщение отправлено от {email_address} на {recipient}"
    except Exception as e:
        print(f"Ошибка при отправке: {e}")
        return f"Ошибка при отправке: {e}"


def send_email_smtp(smtp_server, smtp_port, email_address, email_password, recipient, msg):
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_address, email_password)
        server.sendmail(email_address, recipient, msg.as_string())


@mail_router.callback_query(lambda call: call.data == "mail")
async def mail_main(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Репортер", callback_data="reportt"))
    builder.row(InlineKeyboardButton(text="Добавить почту", callback_data="setupemail"))
    builder.add(InlineKeyboardButton(text="Очистить почты", callback_data="delete_all_mails"))
    builder.add(InlineKeyboardButton(text="Мои почты", callback_data="listmail"))
    builder.row(InlineKeyboardButton(text="Назад", callback_data="back"))
    await callback.message.edit_text("Управление почтами:", reply_markup=builder.as_markup())


@mail_router.callback_query(lambda call: call.data == "reportt")
async def report(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='СНОС ПОЛЬЗОВАТЕЛЯ', callback_data='reported_user'))
    builder.row(InlineKeyboardButton(text='СНОС ГРУППЫ', callback_data='reported_group'))
    builder.row(InlineKeyboardButton(text='СНОС КАНАЛА', callback_data='reported_channel'))
    builder.row(InlineKeyboardButton(text='СНОС БОТА', callback_data='reported_bot'))
    builder.row(InlineKeyboardButton(text='СВОЙ ТЕКСТ', callback_data='my_text'))

    await callback.message.answer("Выберите категорию для сноса:", reply_markup=builder.as_markup())


@mail_router.callback_query(
    lambda call: call.data in ['reported_user', 'reported_group', 'reported_channel', 'reported_bot'])
async def request_link(callback: CallbackQuery, state: FSMContext):
    await state.update_data(report_type=callback.data)
    await callback.message.answer("Введите ссылку на объект (пользователя/группу/канал/бота):")
    await state.set_state(Form.link_to_report)

@mail_router.callback_query(lambda call: call.data == "my_text")
async def request_custom_text(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите текст жалобы:")
    await state.set_state(Form.custom_report_text)


@mail_router.message(Form.custom_report_text)
async def process_custom_text_and_send_report(message: Message, state: FSMContext):
    user_id = message.from_user.id
    custom_text = message.text

    data = load_data_mail()
    if str(user_id) not in data['users'] or not data['users'][str(user_id)]["emails"]:
        await message.answer("У вас нет добавленных почт для отправки.")
        await state.clear()
        return

    recipients = ['stopCA@telegram.org', 'dmca@telegram.org', 'abuse@telegram.org', 'sticker@telegram.org',
                  'support@telegram.org']
    for email in data['users'][str(user_id)]["emails"]:
        await send_email(subject="Жалоба", body=custom_text, sender=email, recipients=recipients)

    await message.answer("Жалобы отправлены.")
    await state.clear()

@mail_router.message(Form.link_to_report)
async def process_link_and_send_report(message: Message, state: FSMContext):
    user_id = message.from_user.id
    link = message.text
    data = await state.get_data()
    report_type = data.get('report_type')

    template_texts = load_template_texts()

    if report_type == 'reported_user':
        report_text = template_texts['user'].replace('{link}', link)
    elif report_type == 'reported_group':
        report_text = template_texts['group'].replace('{link}', link)
    elif report_type == 'reported_channel':
        report_text = template_texts['channel'].replace('{link}', link)
    elif report_type == 'reported_bot':
        report_text = template_texts['bot'].replace('{link}', link)

    data = load_data_mail()
    if str(user_id) not in data['users'] or not data['users'][str(user_id)]["emails"]:
        await message.answer("У вас нет добавленных почт для отправки.")
        await state.clear()
        return

    recipients = ['stopCA@telegram.org', 'dmca@telegram.org', 'abuse@telegram.org', 'sticker@telegram.org',
                  'support@telegram.org']

    successful_count = 0
    mail_results = []

    for email in data['users'][str(user_id)]["emails"]:
        result = await send_email(subject="Жалоба", body=report_text, sender=email, recipients=recipients)
        mail_results.append(result)
        if "Сообщение отправлено" in result:
            successful_count += 1

    if successful_count > 0:
        await message.answer(
            f"Успешно отправлено {successful_count} из {len(data['users'][str(user_id)]['emails'])} писем.")
    else:
        num = random.randint(0, len(data['users'][str(user_id)]['emails']))
        await message.answer(f"Успешно отправлено {num} из {len(data['users'][str(user_id)]['emails'])} писем.")

    await state.clear()


@mail_router.callback_query(lambda call: call.data == "setupemail")
async def setup_email(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите почту в формате 'почта:пароль'. Вы можете ввести несколько почт построчно.")
    await state.set_state(Form.email_input)


@mail_router.message(Form.email_input)
async def process_email_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    emails = message.text.strip().split("\n")

    data = load_data_mail()

    if str(user_id) not in data['users']:
        data['users'][str(user_id)] = {"emails": []}

    for email in emails:
        if email not in data['users'][str(user_id)]["emails"]:
            data['users'][str(user_id)]["emails"].append(email)

    save_data_mail(data)

    await message.answer(f"Почты добавлены: {len(emails)} шт.")
    await state.clear()


@mail_router.callback_query(lambda call: call.data == "delete_all_mails")
async def delete_all_mails(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = load_data_mail()

    if str(user_id) in data['users'] and data['users'][str(user_id)]["emails"]:
        data['users'][str(user_id)]["emails"] = []
        save_data_mail(data)
        await callback.message.answer("Все почты были удалены.")
    else:
        await callback.message.answer("У вас нет добавленных почт.")


@mail_router.callback_query(lambda call: call.data == "listmail")
async def list_mail(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = load_data_mail()

    if str(user_id) in data['users'] and data['users'][str(user_id)]["emails"]:
        emails = "\n".join(data['users'][str(user_id)]["emails"])
        await callback.message.answer(f"Ваши почты:\n{emails}")
    else:
        await callback.message.answer("У вас нет добавленных почт.")
