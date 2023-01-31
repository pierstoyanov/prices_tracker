import os

keyboard = {
    "Type": "keyboard",
    "Buttons": [
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#00FFFF",
            "ActionType": "reply",
            "ActionBody": "dalydata",
            "Text": "Дневни данни",
            "TextOpacity": 60,
            "TextSize": "large"
        },
        {
            "Columns": 1,
            "Rows": 1,
            "BgColor": "#E0FFFF",
            "Text": "<b>LME</b>",
            "ActionType": "open-url",
            "ActionBody": os.environ.get('URL_ONE'),
            "OpenURLType": "internal",
            "Silent": "true",
            "TextSize": "regular",
        },
        {
            "Columns": 1,
            "Rows": 1,
            "BgColor": "#E0FFFF",
            "Text": "<b>LBMA</b>",
            "ActionType": "open-url",
            "ActionBody": os.environ.get('URL_TWO'),
            "OpenURLType": "internal",
            "Silent": "true",
            "TextSize": "regular",
        },
        {
            "Columns": 1,
            "Rows": 1,
            "BgColor": "#E0FFFF",
            "Text": "<b>Westmetal</b>",
            "ActionType": "open-url",
            "ActionBody": os.environ.get('URL_THREE'),
            "OpenURLType": "internal",
            "Silent": "true",
            "TextSize": "regular",
        },
        {
            "Columns": 1,
            "Rows": 1,
            "BgColor": "#E0FFFF",
            "Text": "<b>BNB</b>",
            "ActionType": "open-url",
            "ActionBody": os.environ.get('URL_FOUR'),
            "OpenURLType": "internal",
            "Silent": "true",
            "TextSize": "regular",
        },
        {
            "Columns": 1,
            "Rows": 1,
            "BgColor": "#E0FFFF",
            "Text": "<b>IBEX</b>",
            "ActionType": "open-url",
            "ActionBody": os.environ.get('URL_FIVE'),
            "OpenURLType": "internal",
            "Silent": "true",
            "TextSize": "regular",
        },
        {
            "Columns": 1,
            "Rows": 1,
            "BgColor": "#90EE90",
            "ActionType": "info",
            "ActionBody": "info",
            "Text": "&#128712",
            "TextSize": "large"
        },
    ]
}

welcome_keyboard = {
    "Type": "keyboard",
    "Buttons": [{
        "Columns": 6,
        "Rows": 1,
        "BgColor": "#00FF00",
        "ActionType": "reply",
        "ActionBody": "subscribe",
        "Text": "Aбониране",
        "TextSize": "large"
    }
    ]
}
