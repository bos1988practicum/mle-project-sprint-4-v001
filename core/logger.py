import logging
import sys

# Добавляем логгирование
def add_logger():
    msg_format = "%(asctime)s | %(levelname)s | %(filename)s:%(funcName)s:%(lineno)d - %(message)s"
    logger = logging.getLogger()
    formatter = logging.Formatter(msg_format)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


logger = add_logger()