from email import message
import os
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from bot.messages import static_messages
from bot.messages.message_manager import MessageManager
from bot.users.composite_user_actions import CompositeUserActions
from logger.logger import logging
from storage.storage_manager import storage_manager as sm


# begin bot class
class Bot:
    bot_configuration = BotConfiguration(
        name=os.environ.get('BOT_NAME'),
        auth_token=os.environ.get('BOT_TOKEN'),
        avatar='http://viber.com/avatar.jpg'
    )
    bot_logger = logging.getLogger(__name__)

    def __init__(self, storage_strategy: int, sheets_service):
        self.viber = Api(self.bot_configuration)
        self.storage_strategy = storage_strategy,
        self.users = CompositeUserActions(sm.get_storage_strategy())
        self.sheets_service = sheets_service
        self.messages = static_messages
        self.message_manager = MessageManager()


    def get_daiy_data_unit(self):
        return self.message_manager.daily_builder.du

    def get_daily_info(self):
        ## functional
        # return build_daily_info(self.sheets_service)
        return self.message_manager.daily

    def request_data(self, requested_data) -> str:
        return self.message_manager.request_data(requested_data)

    def get_last_data(self, *args, **kwargs):
        return self.message_manager.get_daily_data_gsheets(*args, **kwargs)
    