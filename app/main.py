import os
import gc
import threading

from cachetools import TTLCache
from flask import Flask, request, Response
from data_collection.functional.act_requests import data_management_with_requests
from data_collection.template_pattern.act_requests_template_patten import DataManagementWithRequests, DataRequestStoreTemplate, WmDataRequest
from logger.logger import logging
from request_handlers import viber_request_handler

from bot.users.firebasee_user_actions import FirebaseUserActions

from instances import bot, viber

# Logger
app_logger = logging.getLogger(__name__)

# Flask
app = Flask(__name__)


# viber equest cache, ttl = max viber api retry time
cache = TTLCache(50,900)
cache_lock = threading.Lock() 


@app.route('/', methods=['POST'])
def incoming():
    """ Function to handle incoming requests from viber api."""
    
    request_json = request.get_json()
    request_raw_data = request.get_data()
    signature = request.headers.get('X-Viber-Content-Signature')

    # validate signature
    if not viber.verify_signature(
            request_data=request_raw_data,
            signature=signature):
        return Response(status=403)
    
    # get request ID
    id = request_json.get('message_token')

    with cache_lock:
        if id in cache:
            # return 200 to cancel firther re-try calls
            return Response(status=200)
        # add id to cache
        cache[id] = True

    # request to viber request object
    viber_request = viber.parse_request(request_raw_data)

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
    users = bot.users.get_all_user_ids()
    # app_logger.info('Users id\'s are: %s', users)

    # daly data
    daily = bot.build_daily_info()

    # check Gcloud scheduler header
    job_name = os.environ.get('SEND_JOB')
    gc_scheduler = 'X-CloudScheduler-JobName'

    if request.headers.get(gc_scheduler) == job_name:
        count = len(users)
        for u in users:
            tokens = viber.send_messages(u, [
                bot.messages.msg_text_w_keyboard(daily),
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

    # viber.unset_webhook()
    webhook_events = ['message', 'subscribed',
                      'unsubscribed', 'conversation_started']
    result = viber.set_webhook(
        url=os.environ['WEBHOOK'], webhook_events=webhook_events)
    app_logger.info('Webhook response: %s', result)
    return Response(status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)  # debug=True
