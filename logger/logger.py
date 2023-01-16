import logging
from logger.CustomFormatter import CustomFormatter

# Imports the Cloud Logging client library
import google.cloud.logging

# logger
log_format = '[%(asctime)s-%(levelname)s-%(name)s]: %(message)s'
console_format = '[%(levelname)s-%(name)s]: %(message)s'

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    # filename='./log/debug.log',
    # filemode='a'
)

console_logger = logging.StreamHandler()
console_logger.setLevel(logging.DEBUG)
console_logger.setFormatter(CustomFormatter())
logging.getLogger('').addHandler(console_logger)


# Instantiates a client
client = google.cloud.logging.Client()

# Retrieves a Cloud Logging handler based on the environment
# you're running in and integrates the handler with the
# Python logging module. By default, this captures all logs
# at INFO level and higher
client.setup_logging()
