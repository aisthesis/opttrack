"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Save options quotes to mongodb
"""

from . import config
from . import constants
from .dbtools import insert_many

def savequotes(quotes, logger, client):
    logger.info('saving {} quotes'.format(len(quotes)))
    dbname = constants.DB[config.ENV]['name']
    db = client[dbname]
    insert_many(logger, db.get_collection('quotes'), quotes)
