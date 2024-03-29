import os
import gc

# from dotenv import load_dotenv
from flask import Flask, request, Response

from data_collection.functional.act_requests import data_management_with_requests
from data_collection.template_pattern.act_requests_template_patten import DataManagementWithRequests
from logger.logger import logging
from request_handlers import viber_request_handler
from bot import bot
from bot.daly_data import build_daly_info
from bot.messages import msg_text_w_keyboard
from bot.users_actions import get_users_id

# Logger
app_logger = logging.getLogger(__name__)

# Flask
app = Flask(__name__)

# viber bot
viber = bot.viber


@app.route('/', methods=['POST'])
def incoming():
    """ Function to handle incoming requests from viber api."""
    app_logger.debug("received request. %s", request.get_data())

    if not viber.verify_signature(
            request.get_data(),
            request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    # request to viber request object
    viber_request = viber.parse_request(request.get_data())
    # handle the request here
    response = viber_request_handler(viber_request)
    return response


@app.route('/collectdata', methods=['GET'])
def get_data():
    # check GCloud scheduler header
    job_name = os.environ.get('GATHER_JOB')
    gc_scheduler = 'X-CloudScheduler-JobName'

    # selector variable that chooses between
    # act_requests and act_requests_template_pattern
    use_functional = False

    if request.headers.get(gc_scheduler) == job_name:
        if use_functional:
            data_management_with_requests()
            gc.collect()
            return Response(status=200)
        else:
            result = DataManagementWithRequests().run()
            if result == 0:
                return Response(status=200)
    return Response(status=500)


@app.route('/sendmsg', methods=['GET'])
def send_msg():
    # users
    users = get_users_id()
    app_logger.info('Users id\'s are: %s', users)

    # daly data
    daly = build_daly_info()

    # check Gcloud scheduler header
    job_name = os.environ.get('SEND_JOB')
    gc_scheduler = 'X-CloudScheduler-JobName'

    if request.headers.get(gc_scheduler) == job_name:
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


@app.route('/register', methods=['GET'])
def register():
    """Function to register webhook to viber"""
    # 'delivered', 'seen', 'failed', 'subscribed',
    # 'unsubscribed', 'conversation_started'
    webhook_events = ['message', 'seen', 'subscribed',
              'unsubscribed', 'conversation_started', 'webhook']
    result = viber.set_webhook(os.environ['WH'],
                               webhook_events = webhook_events)
    app_logger.info('Webhook response: %s', result)
    return Response(status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
