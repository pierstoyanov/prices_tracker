import json
import os

# import bot
from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import TextMessage
from viberbot.api.viber_requests import ViberMessageRequest, ViberSubscribedRequest, ViberFailedRequest, \
    ViberConversationStartedRequest


from bot import bot
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


@app.route('/', methods=['POST'])
def incoming():
    app_logger.debug(f"received request. post data: {request}")

    # handle the request here
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())
    print(viber.get_account_info())

    if isinstance(viber_request, ViberMessageRequest):
        print(viber_request)
        message = viber_request.message
        # lets echo back
        viber.send_messages(viber_request.sender.id, [
            message
        ])
    elif isinstance(viber_request, ViberConversationStartedRequest):
        user = json.load(viber_request.user)
        print(user)
        user_id = user.get('id')
        user_name = user.get('name')

        bot.add_new_user([user_id, user_name])

        viber.send_messages(user_id, [
            # TODO: localise messages
            TextMessage(text=f"Welcome, {user_name}")
        ])
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.get_user.id, [
            TextMessage(text="thanks for subscribing!")
        ])
    elif isinstance(viber_request, ViberFailedRequest):
        app_logger.warning(f"client failed receiving message. failure: {viber_request.get_data()}")

    return Response(status=200)


if __name__ == '__main__':
    # contex = ()
    # ssl_context = context
    # users = viber.get_online()
    # viber.send_messages(to=users, messages=[TextMessage(text='sample')])
    app.run(debug=True, host='localhost', port=8080)
    viber.set_webhook('')
