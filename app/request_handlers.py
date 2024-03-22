import re
from flask import Response
from viberbot.api.viber_requests import ViberRequest, ViberMessageRequest, \
    ViberSubscribedRequest, ViberConversationStartedRequest, \
    ViberUnsubscribedRequest, ViberDeliveredRequest, ViberSeenRequest
from app.bot.messages.request_data import check_valid_date
from instances import bot, viber
from logger.logger import logging

# logger
handler_logger = logging.getLogger(__name__)


def use_regex(input_text):
    pattern = re.compile(r"^([0-9]{2}-[0-9]{2}-[1-2][0-9]{3})$", re.IGNORECASE)
    return pattern.match(input_text)


def handle_message(viber_request: ViberMessageRequest):
    """Handler for generic message request object
    :return: Response object"""

    def handle_subscribe():
        bot.users.add_new_user(viber_request.sender.id, viber_request.sender)
        viber.send_messages(viber_request.sender.id, [
            bot.messages.msg_subbed(viber_request.sender),
        ])

    def handle_daily_data():
        daily = bot.build_daily_info()
        viber.send_messages(viber_request.sender.id, [
            bot.messages.msg_text_w_keyboard(daily),
        ])

    def handle_msg_info():
        viber.send_messages(viber_request.sender.id, [
            bot.messages.msg_info(),
        ])

    message_dict = {
        'subscribe': handle_subscribe,
        'dailydata': handle_daily_data,
        'info': handle_msg_info
    }

    message = viber_request.message.text
    try:
        if message in message_dict:
            message_dict[message]()
            return Response(status=200)
        elif re.match(r"^([0-9]{2}/[0-9]{2}/[1-2][0-9]{3})$", message):
            date_check = check_valid_date(message)  # '' or error message
            if date_check:
                viber.send_messages(
                    viber_request.sender.id, [
                        bot.messages.msg_text_w_keyboard(date_check)
                    ])
                return Response(status=200)
            else:
                viber.send_messages(
                    viber_request.sender.id, [
                        bot.messages.msg_text_w_keyboard(bot.request_data(message))
                    ])
                return Response(status=200)
        else:
            viber.send_messages(viber_request.sender.id, [
                bot.messages.msg_unknown()
            ])
            return Response(status=200)
    except Exception as e:
        handler_logger.error('Error: %s', e)
        return Response(status=500)


def handle_conversation_started(viber_request: ViberConversationStartedRequest):
    """Handler for conversation started request object"""
    try:
        viber.send_messages(viber_request.user.id, [
            bot.messages.msg_welcome_keyboard()
        ])
        return Response(status=200)
    except Exception as e:
        handler_logger.error('Error: %s', e)
        return Response(status=500)


def handle_subscribed(viber_request: ViberSubscribedRequest):
    """Handler for subscribed request object
    :return: Response object"""

    # register user
    result = bot.users.add_new_user(viber_request.user)

    # reply
    viber.send_messages(viber_request.user.id, [
        bot.messages.msg_subbed(viber_request.user),
        bot.messages.msg_user_keyboard()
    ])

    if not result:
        return Response(status=500)
    return Response(status=200)


def handle_unsubscribed(viber_request: ViberUnsubscribedRequest):
    """Handler for unsubscribed request object
    :return: Response object"""

    # unregister user
    result = bot.users.remove_user(viber_request.user_id)
    if not result:
        return Response(status=500)
    return Response(status=200)


def handle_delivered(viber_request: ViberDeliveredRequest):
    handler_logger.info('User %s received %s',
                        viber_request.user_id, viber_request.message_token)
    return Response(status=200)


def handle_seen(viber_request: ViberSeenRequest):
    handler_logger.info('User %s seen %s',
                        viber_request.user_id, viber_request.message_token)
    return Response(status=200)


def handle_viber_request(viber_request: ViberRequest):
    """Action for generic viber request class"""
    handler_logger.info('Received: %s, at: %s ',
                        viber_request.event_type, viber_request.timestamp)
    return Response(status=200)


def viber_request_handler(viber_request):
    """Handler for all request objects"""

    viber_request_handlers = {
        "ViberMessageRequest": handle_message,
        "ViberConversationStartedRequest": handle_conversation_started,
        "ViberSubscribedRequest": handle_subscribed,
        "ViberUnsubscribedRequest": handle_unsubscribed,
        "ViberDeliveredRequest": handle_delivered,
        "ViberSeenRequest": handle_seen,
        "ViberRequest": handle_viber_request
    }

    viber_request_type = viber_request.__class__.__name__
    if viber_request_type in viber_request_handlers:
        return viber_request_handlers[viber_request_type](viber_request)
    else:
        handler_logger.error("Unknown request type: %s", viber_request_type)
        return Response(status=500)
