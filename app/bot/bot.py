import os
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import TextMessage
from app.bot.users.google_sheets_user_actions import GoogleSheetsUserActions
from bot.users.composite_user_actions import CompositeUserActions
from bot.users.firebasee_user_actions import FirebaseUserActions

from logger.logger import logging
from google_sheets.google_service import \
    build_google_service, build_default_google_service

# google api service instance for using sheets
sheets_service = build_default_google_service()

bot_logger = logging.getLogger('bot')

bot_configuration = BotConfiguration(
    name=os.environ.get('BOT_NAME'),
    auth_token=os.environ.get('BOT_TOKEN'),
    avatar='http://viber.com/avatar.jpg'
)

# begin bot class
class Bot:
    bot_configuration = BotConfiguration(
        name=os.environ.get('BOT_NAME'),
        auth_token=os.environ.get('BOT_TOKEN'),
        avatar='http://viber.com/avatar.jpg'
    )

    def __init__(self, storage_strategy: str):
        self.viber = Api(self.bot_configuration)
        self.bot_logger = logging.getLogger('bot'),
        self.storage_strategy = storage_strategy,
        self.users = CompositeUserActions(storage_strategy)
        
    def viber(self):
        return self.viber

    def daily_data(self):
        pass

    def request_data(self):
        pass
