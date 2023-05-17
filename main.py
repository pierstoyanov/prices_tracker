import gc
import os
import re

from flask import Flask, request, Response
from viberbot.api.viber_requests import ViberMessageRequest, ViberSubscribedRequest, ViberFailedRequest, \
    ViberConversationStartedRequest, ViberUnsubscribedRequest, ViberDeliveredRequest, ViberSeenRequest

from bot import bot
from bot.daly_data import build_daly_info
from bot.messages import *
from bot.request_data import build_requested_day_info, check_valid_date
from bot.users_info import add_new_user, remove_user, get_users_id
from data_collection.act_requests import data_management_with_requests

from logger.logger import logging

# logger
app_logger = logging.getLogger(__name__)

# Flask
app = Flask(__name__)

# viber bot
viber = bot.viber


def use_regex(input_text):
    pattern = re.compile(r"^([0-9]{2}-[0-9]{2}-[1-2][0-9]{3})$", re.IGNORECASE)
    return pattern.match(input_text)


@app.route('/', methods=['POST'])
def incoming():
    app_logger.debug("received request. %s", request.get_data())

    # handle the request here
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberDeliveredRequest):
        app_logger.info('User %s received %s', viber_request.user_id, viber_request.message_token)
    elif isinstance(viber_request, ViberSeenRequest):
        app_logger.info('User %s seen %s',  viber_request.user_id, viber_request.message_token)
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
        elif re.match(r"^([0-9]{2}/[0-9]{2}/[1-2][0-9]{3})$", message):
            date_check = check_valid_date(message)
            if date_check:
                viber.send_messages(
                    viber_request.sender.id, [
                        msg_text_w_keyboard(date_check)
                    ]
                )
            else:
                day_data = build_requested_day_info(message)
                viber.send_messages(
                    viber_request.sender.id, [
                        msg_text_w_keyboard(day_data)
                    ]
                )
        elif message == "info":
            viber.send_messages(
                viber_request.sender.id, [
                    msg_info()
                ]
            )
        else:
            viber.send_messages(
                viber_request.sender.id, [
                    msg_unknown()
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
        app_logger.warning("client failed receiving message. failure: %s", viber_request.get_data())

    return Response(status=200)


@app.route('/collectdata', methods=['GET'])
def get_data():
    # check GAE scheduler header
    job_name = os.environ['GATHER_JOB']
    gc_scheduler = 'X-CloudScheduler-JobName'

    if request.headers.get(gc_scheduler) == job_name:
        data_management_with_requests()
        gc.collect()
        return Response(status=200)


@app.route('/sendmsg', methods=['GET'])
def send_msg():
    # users
    users = get_users_id()
    app_logger.info('Users id\'s are: %s', users)

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
