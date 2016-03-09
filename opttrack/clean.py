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

SERVICE_NAME = 'clean'

def clean_all():
    logger = getlogger(SERVICE_NAME)
    for collname in COLLS:
        clean(collname, logger)

def clean(collname, logger=None):
    if not logger:
        logger = getlogger(SERVICE_NAME)
    job(logger, partial(_clean, collname))

def _clean(collname, logger, client):
    coll = getcoll(client, collname)
    msg = "finding duplicate records in collection '{}'".format(collname)
    print(msg)
    logger.info(msg)
    _id = {}
    for key in COLLS[collname]['keys']:
        _id[key[0]] = '${}'.format(key[0])
    pipeline = [
        {"$group": {"_id": _id, "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
        ]
    duplicates = coll.aggregate(pipeline)
    _rm_dups(logger, coll, duplicates)

def _rm_dups(logger, coll, duplicates):
    n_removed = 0
    for item in duplicates:
        n_toremove = item['count'] - 1
        for i in range(n_toremove):
            result = coll.delete_one(item['_id'])
            n_removed += result.deleted_count
    msg = '{} duplicate record(s) found and removed'.format(n_removed)
    print(msg)
    logger.info(msg)

if __name__ == '__main__':
    clean_all()
