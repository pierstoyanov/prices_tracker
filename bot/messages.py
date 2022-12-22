import os

from viberbot.api.messages import TextMessage, KeyboardMessage
from bot.keyboards import keyboard, welcome_keyboard


def msg_wellcome(u):
    return TextMessage(
        text=f"Здравей, {u.name}!\nЗа да се абонираш за бота, отговори на това съобщение със случаен текст.")


def msg_welcome_keyboard():
    return KeyboardMessage(tracking_data='tracking_data', keyboard=welcome_keyboard)


def msg_user_keyboard():
    return KeyboardMessage(tracking_data='tracking_data', keyboard=keyboard)


def msg_subbed(u):
    return TextMessage(
        text=f"{u.name},\nБлагодаря за абонамента!")


def msg_unsubbed():
    return TextMessage(
        text=f"Успешно отписване!")


def msg_text(text: str):
    return TextMessage(text=text)
