import logging
import os
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import TextMessage, RichMediaMessage

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
