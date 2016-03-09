"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Tools for working with mongo
============================

.. currentmodule:: dbtools
"""

from pymongo.errors import BulkWriteError, DuplicateKeyError

from . import config
from . import constants
from .indices import COLLS

def insert_many(logger, coll, entries):
    bulk = coll.initialize_unordered_bulk_op()
    for entry in entries:
        bulk.insert(entry)
        logger.debug('{} queued for insertion'.format(entry))
    try:
        result = bulk.execute()
    except BulkWriteError:
        logger.exception("error writing to database")
        raise
    else:
        logger.info('{} records saved'.format(result['nInserted']))

def getcoll(client, collname, **kwargs):
    dbname = constants.DB[config.ENV]['name']
    _db = client[dbname]
    return _db.get_collection(collname, **kwargs)
    
def create_index(collname, logger, client):
    create_indices([collname,], logger, client)

def create_indices(collnames, logger, client):
    for collname in collnames:
        coll = getcoll(client, collname)
        logger.info("creating index on collection '{}'".format(collname))
        try:
            coll.create_index(**COLLS[collname])
        except DuplicateKeyError:
            logger.exception("index creation on '{}' failed: {}".format(collname, COLLS[collname]))
        else:
            logger.info("index on '{}' created: {}".format(collname, COLLS[collname]))

