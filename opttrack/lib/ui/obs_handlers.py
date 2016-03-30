"""
Copyright (c) 2015 Marshall Farrier
license http://opensource.org/licenses/MIT

lib/ui/handlers.py

Handlers for find menu
"""

from functools import partial

import pynance as pn

from ..dbtools import find_job, update_job
from ..dbwrapper import job
from ..spreads.optspread import UnfinalizedPrice
from ..spreads.optspread_factory import OptSpreadFactory

SEP_LEN = 48

class ObsHandlers(object):

    def __init__(self, logger, tz):
        self.logger = logger
        self.tz = tz
        self.spread_factory = OptSpreadFactory(self.tz)

    def obs(self, spread_type):
        wrapped_spreads = self._get(spread_type)
        self._show_updated(wrapped_spreads)
        return True

    def _get(self, spread_type):
        cursor = job(self.logger, partial(find_job, 'observe', {'Spread_Type': spread_type}))
        wrapped_spreads = {}
        for record in cursor:
            spread = self.spread_factory.make(record)
            if spread.is_alive():
                wrapped_spread = {'spread': spread, '_id': record['_id']}
                if spread.Underlying not in wrapped_spreads:
                    wrapped_spreads[spread.Underlying] = []
                wrapped_spreads[spread.Underlying].append(wrapped_spread)
            else:
                print('dead spread found for {}'.format(spread.Underlying))
                #TODO delete from db
        return wrapped_spreads
        
    def _show_updated(self, wrapped_spreads):
        equities = sorted(wrapped_spreads.keys())
        to_show = []
        for equity in equities:
            self._update_foreq(equity, wrapped_spreads)
            to_show.extend(wrapped_spreads[equity])
        _show_wrapped_spreads(to_show)

    def _update_foreq(self, equity, wrapped_spreads):
        print('Updating spreads for {}'.format(equity))
        print('Getting options data')
        optdata = pn.opt.get(equity)
        eqdata = None
        update_in_mongo = []
        for wrapped_spread in wrapped_spreads[equity]:
            try:
                if wrapped_spread['spread'].update(optdata, eqdata):
                    update_in_mongo.append(wrapped_spread)
            except UnfinalizedPrice:
                earliest_expiry = wrapped_spread['spread'].earliest_expiry()
                print('Getting equity data')
                eqdata = pn.data.get(equity, earliest_expiry.replace(hour=0), None)
                if wrapped_spread['spread'].update(optdata, eqdata):
                    update_in_mongo.append(wrapped_spread)
        self._update_in_db(update_in_mongo)

    def _update_in_db(self, wrapped_spreads):
        if not wrapped_spreads:
            return
        print('{} spread(s) include an expired option, updating database'.format(len(wrapped_spreads)))
        filters, update_docs = _get_update_queries(wrapped_spreads)
        _, n_modified = job(self.logger, partial(update_job, 'observe', filters, update_docs))
        print('Database updated for {} spread(s)'.format(n_modified))

def _get_update_queries(wrapped_spreads):
    filters = []
    update_docs = []
    for wrapped_spread in wrapped_spreads:
        filters.append({'_id': wrapped_spread['_id']})
        update_docs.append({
                '$set': {
                    'Long': wrapped_spread['spread'].Long,
                    'Short': wrapped_spread['spread'].Short},
                '$currentDate': {'lastModified': True},
                })
    return filters, update_docs

def _show_wrapped_spreads(wrapped_spreads):
    if not len(wrapped_spreads):
        print('No spreads to show')
        return
    for wrapped_spread in wrapped_spreads:
        print('-' * SEP_LEN)
        wrapped_spread['spread'].show(True, True, False, True)
    print('=' * SEP_LEN)
    
