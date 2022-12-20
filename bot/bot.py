import os
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import TextMessage, RichMediaMessage

from g_sheets.google_api_operations import get_last_row_values
from logger.logger import logging
from g_sheets.google_service import build_google_service


# logger
bot_logger = logging.getLogger('bot')

# google api service instance for using sheets
sheets_service = build_google_service(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))

bot_configuration = BotConfiguration(
    name=os.environ['BOT_NAME'],
    auth_token=os.environ['BOT_TOKEN'],
    avatar='http://viber.com/avatar.jpg'
)

# viber
viber = Api(bot_configuration)
# viber.set_webhook('https://26e0-79-100-153-222.eu.ngrok.io')


# messages
text_message = TextMessage(text='Sample msg!')

# daily_data
spreadsheet_id = os.environ['SPREADSHEET_DATA']
copper = get_last_row_values(service=sheets_service,
                             spreadsheet_id=spreadsheet_id,
                             sheet_name='copper').get('values')
silver = get_last_row_values(service=sheets_service,
                             spreadsheet_id=spreadsheet_id,
                             sheet_name='silver',
                             end_col='B')
