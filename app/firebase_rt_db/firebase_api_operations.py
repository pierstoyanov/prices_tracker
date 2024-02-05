# logger
from logger.logger import logging
frb_logger = logging.getLogger(__name__)

def firebase_error_handler(func):
    """"Wrapper to handle Firebase api errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            frb_logger.error('Firebase HTTP error occurred %s', e)
            return e

    return wrapper

@firebase_error_handler
def get_all_keys(ref, no_data=False):
    # keys = ref.get().keys()
    keys = ref.get(shallow=no_data)
    return keys


@firebase_error_handler
def get_all_keys_no_data(ref):
    return get_all_keys(ref, no_data=True)


@firebase_error_handler
def add_key(ref, key, key_data):
    ref.child(key).set(key_data)


@firebase_error_handler
def get_key(ref, key):
    child = ref.child(key).get()
    if child is None:
        return None
    return child


@firebase_error_handler
def update_key(ref, key, data_to_add):
    ref.child(key).update(data_to_add)


@firebase_error_handler
def remove_key(ref, key):
    ref.child(key).delete()
    