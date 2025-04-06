from viberbot.api.messages import TextMessage, KeyboardMessage
from bot.messages.keyboards import keyboard, welcome_keyboard


info_txt = "✅ pspricesbot © изпраща дневна информация в 09:00.\n" \
           "✅ За конкретна дата въведете ден във формат  *'дд/мм/гггг'*.\n" \
           "✅ Плъзнете наляво ⬅️ за допълнителни настройки" \
           "от Viber (тихо доставяне, отписване)."
wrong = "Подадената дата е грешна\u2757 \n"
wrong_day = "\u2B55 Денят е невалиден.\n"
wrong_month = "\u2B55 Месецът е невалиден.\n"
wrong_year = "\u2B55 Годината е невалидна.\n"
unknown_txt = "Неразпозната команда. За повече информация натиснете: \u2139."


def msg_welcome_keyboard():
    return KeyboardMessage(tracking_data='tracking_data',
                           keyboard=welcome_keyboard)


def msg_user_keyboard():
    return KeyboardMessage(tracking_data='tracking_data',
                           keyboard=keyboard)


def msg_subbed(u):
    return TextMessage(keyboard=keyboard,
                       text=f"{u.name},\nБлагодаря за абонамента!\n" + info_txt)


def msg_info():
    return TextMessage(keyboard=keyboard,
                       text=info_txt)


def msg_text_w_keyboard(text: str):
    return TextMessage(text=text, keyboard=keyboard)


def msg_text(text: str):
    return TextMessage(text=text)


def msg_unknown():
    return TextMessage(keyboard=keyboard,
                       text=unknown_txt)
