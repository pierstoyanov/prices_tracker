import os
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import TextMessage

from logger.logger import logging
from google_sheets.google_service import \
    build_google_service, build_default_google_service


# logger
bot_logger = logging.getLogger('bot')

# google api service instance for using sheets
sheets_service = build_default_google_service()

bot_configuration = BotConfiguration(
    name=os.environ.get('BOT_NAME'),
    auth_token=os.environ.get('BOT_TOKEN'),
    avatar='http://viber.com/avatar.jpg'
)

# viber
viber = Api(bot_configuration)

# messages
text_message = TextMessage(text='Sample msg!')
