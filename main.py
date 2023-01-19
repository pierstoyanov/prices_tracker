import os

from flask import Flask, request, Response
from viberbot.api.viber_requests import ViberMessageRequest, ViberSubscribedRequest, ViberFailedRequest, \
    ViberConversationStartedRequest, ViberUnsubscribedRequest

from bot import bot
from bot.daly_data import build_daly_info
from bot.messages import msg_subbed, msg_welcome_keyboard, msg_user_keyboard, msg_text
from bot.users_info import add_new_user, remove_user, get_users_id
from data_collection.actions import data_management, data_management_with_requests
from logger.logger import logging

# from scheduler import scheduler
# from scheduler.scheduler import send_daly_msg

# logger
app_logger = logging.getLogger(__name__)

# Flask
app = Flask(__name__)

# viber bot
viber = bot.viber

# daly data
daly = build_daly_info()

# users
users = get_users_id()
app_logger.info(f'Users id\'s are: {users}')

# # scheduler
# scheduler.scheduler.add_job(lambda: data_management(),
#                             scheduler.trigger)
#
#
# scheduler.scheduler.add_job(lambda: send_daly_msg(
#     viber, users, msg_text(daly)),
#     scheduler.trigger)


@app.route('/', methods=['POST'])
def incoming():
    app_logger.debug(f"received request. headers: {request.headers} body: {request.get_data()}")

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
        elif message == "dalydata":
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


@app.route('/collectdata', methods=['GET'])
def get_data():
    # check GAE scheduler header
    job_name = os.environ['GATHER_JOB']
    header_name = f'X-CloudScheduler-JobName'

    if request.headers.get('X-CloudScheduler-JobName') == job_name:
        data_management_with_requests()
        return Response(status=200)
    else:
        return Response(status=403)


@app.route('/sendmsg', methods=['GET'])
def send_msg():
    # check GAE cron header
    if request.headers.get('X-Appengine-Cron'):
        count = len(users)
        for u in users:
            tokens = viber.send_messages(u, [
                msg_text(daly),
                msg_user_keyboard()
            ])
            if tokens:
                count -= 1
        if count == 0:
            return Response(status=200)
    return Response(status=400)


if __name__ == '__main__':
    # app.run(debug=True, host='localhost', port=8080)
    app.run()
