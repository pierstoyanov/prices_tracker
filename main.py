import os

# import bot
from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import TextMessage
from viberbot.api.viber_requests import ViberMessageRequest, ViberSubscribedRequest, ViberFailedRequest

import logger
import bot
from scheduler import scheduler
import data_collection
from data_collection.data_management import data_management


# Flask
app = Flask(__name__)


# from viber bot
viber = bot.viber


@app.route('/', methods=['POST'])
def incoming():
    logger.logger.debug(f"received request. post data: {request.headers}")

    viber_request = viber.parse_request(request.get_data())
    print(viber.get_account_info())
    # handle the request here
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)


    if isinstance(viber_request, ViberMessageRequest):
        print(viber_request)
        message = viber_request.message
        # lets echo back
        viber.send_messages(viber_request.sender.id, [
            message
        ])
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.get_user.id, [
            TextMessage(text="thanks for subscribing!")
        ])
    elif isinstance(viber_request, ViberFailedRequest):
        logger.logger.warning("client failed receiving message. failure: {0}".format(viber_request))

    return Response(status=200)


if __name__ == '__main__':
    # contex = ()
    # ssl_context = context
    # users = viber.get_online()
    # viber.send_messages(to=users, messages=[TextMessage(text='sample')])
    app.run(debug=True, host='localhost', port=8080)
    # viber.set_webhook('https://0284-151-251-240-151.eu.ngrok.io')
