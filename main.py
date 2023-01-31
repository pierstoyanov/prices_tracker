import os
from aifc import Error

from flask import Flask, request, Response
from viberbot.api.viber_requests import ViberMessageRequest, ViberSubscribedRequest, ViberFailedRequest, \
    ViberConversationStartedRequest, ViberUnsubscribedRequest, ViberDeliveredRequest, ViberSeenRequest

from bot import bot
from bot.daly_data import build_daly_info
from bot.messages import msg_subbed, msg_welcome_keyboard, msg_user_keyboard, msg_text_w_keyboard
from bot.users_info import add_new_user, remove_user, get_users_id
from data_collection.act_requests import data_management_with_requests

from logger.logger import logging

# logger
app_logger = logging.getLogger(__name__)

# Flask
app = Flask(__name__)

# viber bot
viber = bot.viber


@app.route('/', methods=['POST'])
def incoming():
    app_logger.debug(f"received request. {request}")

    # handle the request here
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberDeliveredRequest):
        app_logger.info(f'User {viber_request.user_id} received {viber_request.message_token}')
    elif isinstance(viber_request, ViberSeenRequest):
        app_logger.info(f'User {viber_request.user_id} seen {viber_request.message_token}')
    elif isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message.text
        if message == 'subscribe':
            add_new_user(viber_request.sender)

            viber.send_messages(viber_request.sender.id, [
                msg_subbed(viber_request.sender),
            ])
        elif message == "dalydata":
            # daly data
            daly = build_daly_info()
            viber.send_messages(viber_request.sender.id, [
                msg_text_w_keyboard(daly),
            ])
        # TODO data request
        elif message:
            pass
        else:
            viber.send_messages(
                viber_request.sender.id, [
                    msg_user_keyboard()
                ]
            )
    elif isinstance(viber_request, ViberConversationStartedRequest):
        viber.send_messages(viber_request.user.id, [
            msg_welcome_keyboard()
        ])
    elif isinstance(viber_request, ViberSubscribedRequest):
        # register user
        add_new_user(viber_request.user)
        # reply
        viber.send_messages(viber_request.user.id, [
            msg_subbed(viber_request.user),
            msg_user_keyboard()
        ])
    elif isinstance(viber_request, ViberUnsubscribedRequest):
        # de-register user
        remove_user(viber_request.user_id)
    elif isinstance(viber_request, ViberFailedRequest):
        app_logger.warning(f"client failed receiving message. failure: {viber_request.get_data()}")

    return Response(status=200)


@app.route('/collectdata', methods=['GET'])
def get_data():
    # check GAE scheduler header
    job_name = os.environ['GATHER_JOB']
    gc_scheduler = f'X-CloudScheduler-JobName'

    if request.headers.get(gc_scheduler) == job_name:
        try:
            data_management_with_requests()
            return Response(status=200)
        except Error:
            return Response(status=400)
    else:
        return Response(status=403)


@app.route('/sendmsg', methods=['GET'])
def send_msg():
    # users
    users = get_users_id()
    app_logger.info(f'Users id\'s are: {users}')

    # daly data
    daly = build_daly_info()

    # check GAE cron header
    gae_cron = 'X-Appengine-Cron'
    if request.headers.get(gae_cron):
        count = len(users)
        for u in users:
            tokens = viber.send_messages(u, [
                msg_text_w_keyboard(daly),
            ])
            if tokens:
                count -= 1
        if count == 0:
            return Response(status=200)
    return Response(status=400)


if __name__ == '__main__':
    # app.run(debug=True, host='localhost', port=8080)
    # viber.set_webhook("")
    app.run()
