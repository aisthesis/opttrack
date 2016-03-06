"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Connection to MongoDB (:mod:`dbwrapper`)
===================================================

.. currentmodule:: dbwrapper

Opens and closes db connection.
"""
from pymongo import MongoClient

from . import config

def job(logger, fn):
    _client = MongoClient(config.MONGO_CLIENT['host'], config.MONGO_CLIENT['port'])
    logger.info("db connection opened")
    try:
        _ret = fn(logger, _client)
    finally:
        _client.close()
        logger.info("db connection closed")
    return _ret
