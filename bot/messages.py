from viberbot.api.messages import TextMessage, KeyboardMessage
from bot.keyboards import keyboard, welcome_keyboard


def msg_welcome_keyboard():
    return KeyboardMessage(tracking_data='tracking_data', keyboard=welcome_keyboard)


def msg_user_keyboard():
    return KeyboardMessage(tracking_data='tracking_data', keyboard=keyboard)


chk_mrk, left_arr = '\U00002714', '\U00002B05'
info_txt = f"{chk_mrk} pspricesbot изпраща дневна информация 08:55.\n" \
           f"{chk_mrk} За конкретна дата въведете ден във формат 'дд-мм-гггг'.\n" \
           f"{chk_mrk} Плъзнете наляво {left_arr} за натройки на чата" \
           f" от Viber (тихо доставяне, изключване на съобщенията)."


def msg_subbed(u):
    return TextMessage(keyboard=keyboard,
                       text=f"{u.name},\nБлагодаря за абонамента! \n" + info_txt
                       )


def msg_info():
    return TextMessage(keyboard=keyboard,
                       text=info_txt)

def msg_text_w_keyboard(text: str):
    return TextMessage(text=text, keyboard=keyboard)


def msg_text(text: str):
    return TextMessage(text=text)
