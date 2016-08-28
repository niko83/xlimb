# -*- coding: utf-8 -*-

import logging
import os
from app import constants
from logging.handlers import TimedRotatingFileHandler

formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [PID:{0}] [%(name)s]: %(message)s".format(os.getpid())
)


class _NullHandler(logging.Handler):
    def emit(self, record):
        pass


def add_error_handler(logger):
    log_file = os.path.join(constants.LOG_DIR, 'error.log')
    handler = TimedRotatingFileHandler(log_file, when='MIDNIGHT')
    handler.setFormatter(formatter)
    handler.setLevel(logging.ERROR)
    logger.addHandler(handler)


def init_log():

    if not constants.LOG_DIR:
        raise Exception('settigns.LOG_DIR must be defined')

    if not os.path.exists(constants.LOG_DIR):
        os.mkdir(constants.LOG_DIR)
        print('Log dir %s was created' % constants.LOG_DIR)

    for logger_name in ['xlimb', 'stat']:

        logger = logging.getLogger(logger_name)
        logger.setLevel(constants.LOGGER_LEVEL)

        log_file = os.path.join(constants.LOG_DIR, logger_name + '.log')
        handler = TimedRotatingFileHandler(log_file, when='MIDNIGHT')

        handler.setFormatter(formatter)
        handler.setLevel(constants.LOGGER_LEVEL)

        logger.addHandler(handler)
        add_error_handler(logger)
