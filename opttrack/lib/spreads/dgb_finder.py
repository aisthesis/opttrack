"""
./opttrack/lib/spreads/dgb_finder.py

Copyright (c) 2016 Marshall Farrier
license http://opensource.org/licenses/MIT

Find promising diagonal butterfly spreads.

The logic for defining promising spreads is encapsulated
in the function `_meets_criteria()` below.
"""

import locale

import pandas as pd

from .optspread import OptSpread
from .optutils import get_price
from .. import strikes

MIN_RATIO = 1.5

class DgbFinder(object):

    def __init__(self, opts, opt_factory):
        self.opts = opts
        self.opt_factory = opt_factory
        self._diff_filter = _get_diff_filter()

    def run(self):
        # necessary for dealing with comma-grouped strike prices
        prior_loc = locale.getlocale()
        locale.setlocale(locale.LC_ALL, 'en_US')
        nearexpiries = self._get_nearexpiries()
        straddles = self._get_straddles(nearexpiries)
        dgbs = self._get_dgbs(straddles)
        locale.setlocale(locale.LC_ALL, prior_loc)
        return dgbs

    def _get_dgbs(self, straddles):
        dgbs = []
        for straddle in straddles:
            dgbs.extend(self._get_dgbs_for_straddle(straddle))
        return dgbs

    def _get_dgbs_for_straddle(self, straddle):
        expiries = self.opts.exps()[self.opts.exps().slice_indexer(straddle['Expiry'] + 
                self._diff_filter['min'], straddle['Expiry'] + self._diff_filter['max'])]
        dgbs = []
        for expiry in expiries:
            dgbs.extend(self._get_dgbs_for_expiry(straddle, expiry))
        return dgbs

    def _get_dgbs_for_expiry(self, straddle, expiry):
        call_strikes = strikes.allforexp(self.opts, expiry, 'call')
        put_strikes = strikes.allforexp(self.opts, expiry, 'put')
        min_putstrike = straddle['Strike'] - straddle['Price']['total']
        dgbs = []
        call_end_ix = len(call_strikes) - 1
        for put_strike in put_strikes:
            if put_strike < min_putstrike:
                continue
            if put_strike >= straddle['Strike']:
                return dgbs
            strike_diff = straddle['Strike'] - put_strike
            call_ix = strikes.getlastmatched(straddle['Strike'] + strike_diff, call_strikes, call_end_ix)
            # only consider cases where there is a call matching the put
            if call_ix < 0:
                continue
            call_end_ix = call_ix
            strangle = self._get_strangle(straddle, call_strikes[call_ix], put_strike, expiry)
            metrics = _get_metrics(straddle, strangle, strike_diff)
            if _meets_criteria(metrics):
                dgbs.append(self._get_spread(straddle, strangle, metrics))
        return dgbs

    def _get_strangle(self, straddle, call_strike, put_strike, expiry):
        strangle = {'call': {}, 'put': {}}
        strangle['call']['Price'] = get_price(self.opts, 'call', call_strike, expiry)
        strangle['call']['Expiry'] = expiry
        strangle['call']['Strike'] = call_strike
        strangle['put']['Price'] = get_price(self.opts, 'put', put_strike, expiry)
        strangle['put']['Expiry'] = expiry
        strangle['put']['Strike'] = put_strike
        return strangle

    def _get_spread(self, straddle, strangle, metrics):
        underlying = self.opts.data.iloc[0].loc['Underlying']
        spread = OptSpread(underlying, 'dgb', self.opts.data.iloc[0].loc['Underlying_Price'], metrics['Credit'])
        for opt_type in ('call', 'put',):
            spread.buy_one(self.opt_factory.make(strangle[opt_type]['Strike'], strangle[opt_type]['Expiry'],
                    opt_type, strangle[opt_type]['Price'], underlying))
            spread.sell_one(self.opt_factory.make(straddle['Strike'], straddle['Expiry'],
                    opt_type, straddle['Price'][opt_type], underlying))
        return spread

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

def _get_diff_filter():
    # distance between near and far expiry
    diff_filter = {}
    # 3rd Friday range:
    # earliest: 15
    # latest:   21
    # near falls on 02-21, far on 05-16 less 1
    diff_filter['min'] = pd.Timedelta('83 days')
    # near falls on 03-15, far on 06-21 plus 1
    diff_filter['max'] = pd.Timedelta('98 days')
    return diff_filter

def _meets_criteria(metrics):
    # criteria for considering this type of spread
    return metrics['Credit'] > metrics['Risk'] and metrics['Ratio'] >= MIN_RATIO

def _get_metrics(straddle, strangle, strike_diff):
    metrics = {}
    metrics['Near_Price'] = straddle['Price']['total']
    metrics['Far_Price'] = strangle['call']['Price'] + strangle['put']['Price']
    metrics['Credit'] = straddle['Price']['total'] - metrics['Far_Price']
    metrics['Risk'] = strike_diff - metrics['Credit']
    metrics['Ratio'] = straddle['Price']['total'] / metrics['Far_Price']
    return metrics

