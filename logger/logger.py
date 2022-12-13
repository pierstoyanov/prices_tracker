import logging

# logger

log_format = '%(asctime)s-%(levelname)s-%(name)s - %(message)s'

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    filename='logs.log'
)

logger = logging.getLogger(__name__)
