"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Generate default logger
=======================

.. currentmodule:: logutil
"""

import logging
import os

from . import config
from . import constants

def getlogger(service_name):
    logger = logging.getLogger(service_name)
    loglevel = logging.INFO if config.ENV == 'prod' else logging.DEBUG
    logger.setLevel(loglevel)
    log_dir = _getlogdir(service_name)
    handler = logging.FileHandler(os.path.join(log_dir, 'service.log'))
    formatter = logging.Formatter(constants.LOG['format'])
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def _getlogdir(service_name):
    log_dir = os.path.normpath(os.path.join(config.LOG_ROOT, constants.LOG['path'], service_name))
    try:
        os.makedirs(log_dir)
    except OSError:
        if not os.path.isdir(log_dir):
            raise
    return log_dir
