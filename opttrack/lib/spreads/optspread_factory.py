"""
./opttrack/lib/optspread_factory.py

Copyright (c) 2016 Marshall Farrier
license http://opensource.org/licenses/MIT

Factory for creating spreads from assorted inputs,
particularly from records pulled from MongoDB in dictionary
form.
"""

import pytz

from ..stockopt import StockOptFactory
from .optspread import OptSpread

class OptSpreadFactory(object):

    def __init__(self, tz=None):
        self.tz = tz if tz else pytz.timezone('US/Eastern')
        self.opt_factory = StockOptFactory(tz)
        
    def make(self, record):
        # make a spread object from a mongo record
        spread = OptSpread(**record)
        if record['Spread_Type'] == 'dgb':
            self._update_dgb(spread, record)
        return spread

    def _update_dgb(self, spread, record):
        for item in record['Long']:
            spread.buy_one(self.opt_factory.make(**item))
        for item in record['Short']:
            spread.sell_one(self.opt_factory.make(**item))
