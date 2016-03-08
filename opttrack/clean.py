"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Dedupe a collection based on an intended unique index.
"""

from functools import partial

from lib import constants
from lib.indices import COLLS 
from lib.logutil import getlogger
from lib.dbwrapper import job

SERVICE_NAME = 'clean'

def clean(coll):
    logger = getlogger(SERVICE_NAME)
    job(logger, partial(_clean, coll))

def _clean(coll, logger, client):
    # use indices in lib.indices
    pass

if __name__ == '__main__':
    coll = 'track'
    clean(coll)
