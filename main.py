import os

# import bot
from flask import Flask, request, Response
from viberbot.api.viber_requests import ViberMessageRequest, ViberSubscribedRequest, ViberFailedRequest, \
    ViberConversationStartedRequest, ViberUnsubscribedRequest

from bot import bot
from bot.daly_data import build_daly_info
from bot.messages import msg_wellcome, msg_subbed, msg_welcome_keyboard, msg_user_keyboard, msg_text
from bot.users_info import add_new_user, remove_user
from logger.logger import logging

# logger
app_logger = logging.getLogger(__name__)

# Flask
app = Flask(__name__)

# viber bot
viber = bot.viber

# daly data
daly = build_daly_info()


# TODO apply gettext for localisation
@app.route('/', methods=['POST'])
def incoming():
    app_logger.debug(f"received request. post data: {request}")

    # handle the request here
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        # print(viber_request)
        message = viber_request.message.text
        if message == 'Абониране':
            add_new_user(viber_request.user)

            viber.send_messages(viber_request.user.id, [
                msg_subbed(viber_request.user),
                msg_user_keyboard()
            ])

        # lets echo back
        if message == "dalydata":
            viber.send_messages(viber_request.sender.id, [
                msg_text(daly),
                msg_user_keyboard()
            ])
        else:
            viber.send_messages(
                viber_request.sender.id, [
                    msg_user_keyboard()
                ]
            )
    elif isinstance(viber_request, ViberConversationStartedRequest):
        u = viber_request.user
        viber.send_messages(u.id, [
            # msg_wellcome(u),
            msg_welcome_keyboard()
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
    # viber.set_webhook('https://2fd3-151-251-253-15.eu.ngrok.io')
