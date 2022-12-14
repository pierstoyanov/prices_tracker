import logging

from logger.CustomFormatter import CustomFormatter


# logger
log_format = '[%(asctime)s-%(levelname)s-%(name)s]: %(message)s'
console_format = '[%(levelname)s-%(name)s]: %(message)s'

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    filename='./log/debug.log',
    filemode='a'
)

console_logger = logging.StreamHandler()
console_logger.setLevel(logging.DEBUG)
console_logger.setFormatter(CustomFormatter())
logging.getLogger('').addHandler(console_logger)
