import logging

LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"

logging.basicConfig(
    filename="myapp.log",
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    filemode="w",
)

logger = logging.getLogger(__name__)
