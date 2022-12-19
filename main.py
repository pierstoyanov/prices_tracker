import json
import os

# import bot
from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.viber_requests import ViberMessageRequest, ViberSubscribedRequest, ViberFailedRequest, \
    ViberConversationStartedRequest, ViberUnsubscribedRequest

from bot import bot
from bot.messages import msg_wellcome, msg_subbed, msg_unsubbed, \
    msg_welcome_keyboard
from bot.users_info import add_new_user, remove_user
from g_sheets.goog_service import get_goog_service
from logger.logger import logging
from scheduler import scheduler
import data_collection
from data_collection.actions import data_management

# logger
app_logger = logging.getLogger(__name__)

# Flask
app = Flask(__name__)

# viber bot
viber = bot.viber


# TODO apply gettext for localisation
@app.route('/', methods=['POST'])
def incoming():
    app_logger.debug(f"received request. post data: {request}")

    # handle the request here
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())
    # print(viber.get_account_info())

    if isinstance(viber_request, ViberMessageRequest):
        print(viber_request)
        message = viber_request.message
        # lets echo back
        viber.send_messages(viber_request.sender.id, [
            message
        ])
    elif isinstance(viber_request, ViberConversationStartedRequest):
        u = viber_request.user
        viber.send_messages(u.id, [
            # TODO: localise messages
            msg_wellcome(u),
            # msg_welcome_keyboard()
        ])
    elif isinstance(viber_request, ViberSubscribedRequest):
        # register user
        add_new_user(viber_request.user)

        viber.send_messages(viber_request.user.id, [
            msg_subbed(viber_request.user)
        ])
    elif isinstance(viber_request, ViberUnsubscribedRequest):
        # de-register user
        remove_user(viber_request.user_id)
    elif isinstance(viber_request, ViberFailedRequest):
        app_logger.warning(f"client failed receiving message. failure: {viber_request.get_data()}")

    return Response(status=200)


if __name__ == '__main__':
    # contex = ()
    # ssl_context = context
    # users = viber.get_online()
    # viber.send_messages(to=users, messages=[TextMessage(text='sample')])
    app.run(debug=True, host='localhost', port=8080)
    # viber.set_webhook('https://a424-151-251-246-195.eu.ngrok.io')
