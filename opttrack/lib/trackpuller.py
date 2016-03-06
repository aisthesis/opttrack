"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Get options to be tracked
"""

import datetime as dt
from bson.codec_options import CodecOptions

from . import config
from . import constants
from .dbwrapper import job

class TrackPuller(object):

    def __init__(self, logger):
        self.logger = logger

    def get(self):
        """
        Get a dictionary of options to track.
        """
        return job(self.logger, _getactive)

def _getactive(logger, client):
    totrack = {}
    dbname = constants.DB[config.ENV]['name']
    _db = client[dbname]
    c_opts = CodecOptions(tz_aware=True)
    trackcoll = _db.get_collection('track', codec_options=c_opts)
    utcnow = dt.datetime.utcnow()
    for entry in trackcoll.find({'Expiry': {'$gt': utcnow}}):
        _addentry(totrack, entry)
    logger.info('found active track entries for {} equities'.format(len(totrack)))
    return totrack

def _addentry(totrack, entry):
    if entry['Underlying'] not in totrack:
        totrack[entry['Underlying']] = []
    totrack[entry['Underlying']].append({'Opt_Type': entry['Opt_Type'],
        'Strike': entry['Strike'], 'Expiry': entry['Expiry']})
