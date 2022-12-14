import os

keyboard = {
    "Type": "keyboard",
    "Buttons": [
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#2db9b9",
            "ActionType": "reply",
            "ActionBody": "dalydata",
            "Text": "Дневни данни",
            "TextVAlign": "middle",
            "TextHAlign": "center",
            "TextOpacity": 60,
            "TextSize": "regular"
        },
        {
            "Columns": 3,
            "Rows": 1,
            "Text": "<font color=#323232><b>LMA</b></font>",
            "ActionType": "open-url",
            "ActionBody": os.environ.get('URL_ONE'),
            "TextSize": "medium",
            "TextVAlign": "middle",
            "TextHAlign": "left"
        },
        {
            "Columns": 3,
            "Rows": 1,
            "Text": "<font color=#323232><b>LBMA</b></font>",
            "ActionType": "open-url",
            "ActionBody": os.environ.get('URL_TWO'),
            "TextSize": "medium",
            "TextVAlign": "middle",
            "TextHAlign": "left"
        },
    ]
}

welcome_keyboard = {
    "Type": "keyboard",
    "Buttons": [{
        "Columns": 6,
        "Rows": 1,
        "BgColor": "#2db9b9",
        "ActionType": "reply",
        "ActionBody": "Aбониране",
        "Text": "Абониране",
        "TextVAlign": "middle",
        "TextHAlign": "center",
        "TextOpacity": 60,
        "TextSize": "regular"
    }
    ]
}
