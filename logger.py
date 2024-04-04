

import logging
import sys


def setup_logger(name: str, level: str = 'info') -> logging.Logger:
    logging_level = get_log_level(level)
    logger = logging.getLogger(name)
    logger.setLevel(logging_level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def get_log_level(level: str):
    lowercase_level = level.lower()
    if lowercase_level == 'info':
        return logging.INFO
    if lowercase_level == 'debug':
        return logging.DEBUG
    if lowercase_level == 'error':
        return logging.ERROR
    if lowercase_level == 'warning':
        return logging.WARNING
    if lowercase_level == 'critical':
        return logging.CRITICAL
    return logging.INFO
    