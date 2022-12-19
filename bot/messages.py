from viberbot.api.messages import TextMessage, KeyboardMessage

keyboard = {
    "Type": "keyboard",
    "Buttons": [{
        "Columns": 6,
        "Rows": 1,
        "BgColor": "#2db9b9",
        "ActionType": "reply",
        "ActionBody": "Успешно се абонирахте за pspricesbot!",
        "Text": "Абониране",
        "TextVAlign": "middle",
        "TextHAlign": "center",
        "TextOpacity": 60,
        "TextSize": "regular"
        }
    ]
}


def msg_wellcome(u):
    return TextMessage(
        text=f"Добре дошли, {u.name}!\nЗа да се абонираш за бота, отговори на това съобщение със случаен текст.")


def msg_welcome_keyboard():
    return KeyboardMessage(tracking_data='tracking_data', keyboard=keyboard)


def msg_subbed(u):
    return TextMessage(
        text=f"{u.name}, thanks for subscribing!")


def msg_unsubbed():
    return TextMessage(
        text=f"Успешно отписване!")
