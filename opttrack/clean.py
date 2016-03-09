"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Dedupe a collection based on an intended unique index.
"""

from functools import partial

from lib import constants
from lib.indices import COLLS 
from lib.logutil import getlogger
from lib.dbtools import getcoll
from lib.dbwrapper import job

#TODO temporary
from lib.dbtools import create_index, create_indices

SERVICE_NAME = 'clean'

def clean(collnames):
    logger = getlogger(SERVICE_NAME)
    job(logger, partial(create_indices, collnames))

def _clean(collname, logger, client):
    # use indices in lib.indices
    coll = getcoll(client, collname)
    logger.info("creating index on collection '{}'".format(collname))
    coll.create_index(**COLLS[collname])
    logger.info("index on '{}' created: {}".format(collname, COLLS[collname]))

if __name__ == '__main__':
    collnames = ['quotes', 'track', 'watchList']
    clean(collnames)
