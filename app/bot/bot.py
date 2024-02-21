import os
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import TextMessage
from bot.users.composite_user_actions import CompositeUserActions
from bot.messages.daily_data import get_daily_data, build_daily_info
from logger.logger import logging
from storage.storage_manager import storage_manager

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
        self.sheets_service = storage_manager.get_sheets_service()
        
    def viber(self):
        return self.viber

    def daily_data(self, *args, **kwargs):
        return get_daily_data(self.sheets_service, *args, **kwargs)

    def build_daily_info(self):
        return build_daily_info(self.sheets_service)

    def request_data(self):
        pass
