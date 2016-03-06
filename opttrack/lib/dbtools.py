"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Tools for working with mongo
============================

.. currentmodule:: dbtools
"""

from pymongo.errors import BulkWriteError

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
