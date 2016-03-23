"""
./opttrack/lib/spreads/diagonal_butterfly.py

Copyright (c) 2016 Marshall Farrier
license http://opensource.org/licenses/MIT

Find promising diagonal butterfly spreads.
"""

import locale

import pandas as pd

from .optutils import get_price
from .. import strikes

class DiagonalButterfly(object):

    def __init__(self, opts):
        self.opts = opts

    def get(self):
        # necessary for dealing with comma-grouped strike prices
        prior_loc = locale.getlocale()
        locale.setlocale(locale.LC_ALL, 'en_US')
        nearexpiries = self._get_nearexpiries()
        straddles = self._get_straddles(nearexpiries)
        locale.setlocale(locale.LC_ALL, prior_loc)
        return []

    def _get_nearexpiries(self):
        min_exp = self.opts.quotetime() + pd.Timedelta('90 days')
        max_exp = self.opts.quotetime() + pd.Timedelta('135 days')
        return self.opts.exps()[self.opts.exps().slice_indexer(min_exp, max_exp)]

    def _get_straddles(self, expiries):
        straddles = []
        for expiry in expiries:
            straddles.extend(self._get_straddles_forexp(expiry))
        return straddles

    def _get_straddles_forexp(self, expiry):
        """
        The list will normally contain 2 straddles only if the underlying
        price is exactly between 2 strikes. If the underlying is closer to
        1 strike than another, the list will contain only 1 element.
        """
        straddles = []
        all_strikes = strikes.matchedforexp(self.opts, expiry)
        eqprice = self.opts.data.iloc[0].loc['Underlying_Price']
        straddle_strikes = strikes.closest(all_strikes, eqprice)
        for straddle_strike in straddle_strikes:
            call_price = get_price(self.opts, 'call', straddle_strike, expiry)
            put_price = get_price(self.opts, 'put', straddle_strike, expiry)
            straddles.append({
                'Expiry': expiry, 
                'Strike': straddle_strike, 
                'Price': {
                    'call': call_price, 
                    'put': put_price,
                    'total': call_price + put_price}})
        return straddles
