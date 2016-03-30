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
        return result['nInserted']

def delete_many(logger, coll, entry):
    result = coll.delete_many(entry)
    n_deleted = result.deleted_count
    if n_deleted > 0:
        logger.info('{} record(s) deleted'.format(n_deleted))
    else:
        logger.warn('Record not found: {}'.format(entry))
    return n_deleted

def find_job(collname, qry, logger, client, **kwargs):
    # can be passed to dbwrapper.job() using functools.partial
    coll = getcoll(client, collname, **kwargs)
    return coll.find(qry)

def update_job(collname, filters, update_docs, logger, client, **kwargs):
    # can be passed to dbwrapper.job() using functools.partial
    # filters and update_docs must match
    assert len(filters) == len(update_docs)
    coll = getcoll(client, collname, **kwargs)
    n_matched = 0
    n_modified = 0
    logger.info('running {} update queries'.format(len(queries)))
    for i in len(filters):
        result = coll.update_many(filters[i], update_docs[i], **kwargs)
        n_matched += result.matched_count
        n_modified += result.modified_count
    logger.info('{} records modified of {} records matched'.format(n_modified, n_matched))
    return n_matched, n_modified

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

def create_all_indices(logger, client):
    create_indices(COLLS.keys(), logger, client)
