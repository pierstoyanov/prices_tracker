import re

from flask import Response
from viberbot.api.viber_requests import ViberMessageRequest
from bot.bot import viber
from bot.daly_data import build_daly_info
from bot.messages import msg_subbed, msg_text_w_keyboard, msg_info, \
    msg_unknown, msg_welcome_keyboard, msg_user_keyboard
from bot.request_data import check_valid_date, build_requested_day_info
from bot.users_actions import add_new_user, remove_user
from main import app_logger


def use_regex(input_text):
    pattern = re.compile(r"^([0-9]{2}-[0-9]{2}-[1-2][0-9]{3})$", re.IGNORECASE)
    return pattern.match(input_text)


def handle_message(viber_request: ViberMessageRequest):
    """Handler for generic message request object
    :return: Response object"""

    def handle_subscribe():
        add_new_user(viber_request.sender)
        viber.send_messages(viber_request.sender.id, [
            msg_subbed(viber_request.sender),
        ])

    def handle_daily_data():
        daily = build_daly_info()
        viber.send_messages(viber_request.sender.id, [
            msg_text_w_keyboard(daily),
        ])

    messages_dict = {
        'subscribe': handle_subscribe,
        'dailydata': handle_daily_data,
    }

    message = viber_request.message.text
    try:
        if message in messages_dict:
            messages_dict[message]()
            return Response(status=200)
        elif re.match(r"^([0-9]{2}/[0-9]{2}/[1-2][0-9]{3})$", message):
            date_check = check_valid_date(message)
            if date_check:
                viber.send_messages(
                    viber_request.sender.id, [
                        msg_info(),
                        msg_text_w_keyboard(build_requested_day_info(date_check))
                    ])
                return Response(status=200)
        else:
            viber.send_messages(viber_request.sender.id, [
                msg_unknown()
            ])
            return Response(status=200)
    except Exception as e:
        app_logger.error('Error: %s', e)
        return Response(status=500)


def handle_conversation_started(viber_request: ViberMessageRequest):
    """Handler for conversation started request object"""
    try:
        viber.send_messages(viber_request.user.id, [
            msg_welcome_keyboard()
        ])
        return Response(status=200)
    except Exception as e:
        app_logger.error('Error: %s', e)
        return Response(status=500)


def handle_subscribed(viber_request: ViberMessageRequest):
    """Handler for subscribed request object
    :return: Response object"""

    # register user
    result = add_new_user(viber_request.user)

    # reply
    viber.send_messages(viber_request.user.id, [
        msg_subbed(viber_request.user),
        msg_user_keyboard()
    ])

    if not result:
        return Response(status=500)
    return Response(status=200)


def handle_unsubscribed(viber_request: ViberMessageRequest):
    """Handler for unsubscribed request object
    :return: Response object"""

    # unregister user
    result = remove_user(viber_request.user)
    if not result:
        return Response(status=500)
    return Response(status=200)


def handle_delivered(viber_request: ViberMessageRequest):
    app_logger.info('User %s received %s', viber_request.user_id, viber_request.message_token)


def handle_seen(viber_request: ViberMessageRequest):
    app_logger.info('User %s seen %s', viber_request.user_id, viber_request.message_token)


def viber_request_handler(viber_request):
    """Handler for all request objects"""

    viber_request_handlers = {
        "ViberMessageRequest": handle_message,
        "ViberConversationStartedRequest": handle_conversation_started,
        "ViberSubscribedRequest": handle_subscribed,
        "ViberUnsubscribedRequest": handle_unsubscribed,
        "ViberDeliveredRequest": handle_delivered,
        "ViberSeenRequest": handle_seen
    }

    viber_request_type = viber_request.__class__.__name__
    if viber_request_type in viber_request_handlers:
        viber_request_handlers[viber_request_type](viber_request)
    else:
        print("Unknown request type: {}".format(viber_request_type))
