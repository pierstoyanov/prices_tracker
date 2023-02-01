from viberbot.api.messages import TextMessage, KeyboardMessage
from bot.keyboards import keyboard, welcome_keyboard


def msg_welcome_keyboard():
    return KeyboardMessage(tracking_data='tracking_data', keyboard=welcome_keyboard)


def msg_user_keyboard():
    return KeyboardMessage(tracking_data='tracking_data', keyboard=keyboard)


c, chk_mrk, left_arr = '\U000000A9', '\U00002714', '\U00002B05'
info_txt = f"✅ pspricesbot © изпраща дневна информация 08:55.\n" \
           f"✅ За конкретна дата въведете ден във формат 'дд-мм-гггг'.\n" \
           f"✅ Плъзнете наляво ⬅️ за настройки на чата" \
           f" от Viber (тихо доставяне, отписване)."


def msg_subbed(u):
    return TextMessage(keyboard=keyboard,
                       text=f"{u.name},\nБлагодаря за абонамента!\n" + info_txt
                       )


def msg_info():
    return TextMessage(keyboard=keyboard,
                       text=info_txt)


def msg_text_w_keyboard(text: str):
    return TextMessage(text=text, keyboard=keyboard)


def msg_text(text: str):
    return TextMessage(text=text)
