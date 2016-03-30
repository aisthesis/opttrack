"""
./opttrack/lib/spreads/optspread.py

Copyright (c) 2016 Marshall Farrier
license http://opensource.org/licenses/MIT

Generic spread class
"""

import datetime as dt
from functools import reduce

import pytz

from .. import stockopt
from ..utils import safe_divide
from . import optutils

SPREAD_TYPES = {
        'dgb': 'diagonal butterfly',
        'dblcal': 'double calendar',
        }

class UnfinalizedPrice(Exception):
    # raised when option expired with no final price
    pass

class OptSpread(object):

    def __init__(self, equity=None, spread_type=None, eq_price=0., ref_price=0., **kwargs):
        # unconventional capitalization allows use of built-in
        # `vars()` for immediate conversion to an appropriate dict
        if equity:
            assert spread_type in SPREAD_TYPES
            self.Underlying = equity.upper()
            self.Spread_Type = spread_type
            self.Underlying_Price = float(eq_price)
            self.Ref_Price = float(ref_price)
        else:
            for key in kwargs:
                setattr(self, key, kwargs[key])
        self.Long = []
        self.Short = []

    def __str__(self):
        return str(vars(self))

    def get_value(self):
        val, _, _ = self._get_value()
        return val

    def buy_one(self, opt):
        self.Long.append(opt)

    def sell_one(self, opt):
        self.Short.append(opt)

    def buy_many(self, opts):
        self.Long.extend(opts)

    def sell_many(self, opts):
        self.Short.extend(opts)

    def show(self, show_price=True, show_eq_price=True, show_metrics=True, show_perf=False):
        stock_price_txt = ' at {:.2f}'.format(self.Underlying_Price) if show_eq_price else ''
        print('{}{} ({}):'.format(self.Underlying, stock_price_txt, SPREAD_TYPES[self.Spread_Type]))
        if show_perf:
            self.show_perf()
        if show_metrics:
            self.show_metrics()
        for title in ('Long', 'Short',):
            print('{}:'.format(title))
            for opt in getattr(self, title):
                print('  {}'.format(stockopt.get_repr(opt, show_price)))

    def show_perf(self):
        print('Performance:')
        if self.Spread_Type == 'dgb':
            self._show_dgb_perf()
        else:
            print('  not implemented')

    def get_metrics(self):
        if self.Spread_Type == 'dgb':
            return self._get_dgb_metrics()
        return {}

    def show_metrics(self):
        print('Metrics:')
        if self.Spread_Type == 'dgb':
            self._show_dgb_metrics()
        else:
            print('  not implemented')

    def update(self, optdata, eqdata=None):
        # return True if anything was finalized
        self.Underlying_Price = optdata.data.iloc[0].loc['Underlying_Price']
        finalized_any = _update_all(optdata, eqdata, self.Long)
        finalized_any |= _update_all(optdata, eqdata, self.Short)
        return finalized_any

    def is_alive(self):
        # true iff at least one option does not have 'Final_Price': True
        for opt in self.Long:
            if not opt.get('Final_Price', False):
                return True
        for opt in self.Short:
            if not opt.get('Final_Price', False):
                return True
        return False

    def earliest_expiry(self):
        earliest = _get_earliest(self.Long)
        return _get_earliest(self.Short, earliest)

    def _get_value(self):
        long_total = reduce(_add_opt_prices, self.Long) if self.Long else 0.
        short_total = reduce(_add_opt_prices, self.Short) if self.Short else 0.
        return long_total - short_total, long_total, short_total

    def _show_dgb_perf(self):
        perf = self._get_dgb_perf()
        for key in ('profit', 'risk', 'return',):
            print('  {}: {:.2f}'.format(key.capitalize(), perf[key]))

    def _get_dgb_perf(self):
        perf = {}
        perf['risk'] = self.Ref_Price + abs(self.Short[0]['Strike'] - self.Long[0]['Strike'])
        value = self.get_value()
        perf['profit'] = value - self.Ref_Price
        perf['return'] = safe_divide(perf['profit'], perf['risk'])
        return perf

    def _show_dgb_metrics(self):
        metrics = self._get_dgb_metrics()
        for key in ('credit', 'risk', 'ratio',):
            print('  {}: {:.2f}'.format(key.capitalize(), metrics[key]))

    def _get_dgb_metrics(self):
        metrics = {}
        val, long_total, short_total = self._get_value()
        metrics['credit'] = -val
        metrics['ratio'] = safe_divide(short_total, long_total)
        strike_diff = abs(self.Short[0]['Strike'] - self.Long[0]['Strike'])
        metrics['risk'] = strike_diff - metrics['credit']
        return metrics

def _add_opt_prices(opt1, opt2):
    return opt1['Price'] + opt2['Price']

def _update_all(optdata, eqdata, opts):
    finalized_any = False
    for opt in opts:
        finalized_any |= _update_one(optdata, eqdata, opt)
    return finalized_any

def _update_one(optdata, eqdata, opt):
    # extract tzinfo from opt['Expiry']
    if opt.get('Final_Price', False):
        return False
    try:
        price = optutils.get_price(optdata, opt['Opt_Type'], opt['Strike'],
                opt['Expiry'].replace(tzinfo=None, hour=0))
        opt['Price'] = price
        return False
    except KeyError:
        if opt['Expiry'] < pytz.utc.localize(dt.datetime.utcnow()):
            if eqdata is None or opt['Expiry'] < opt['Expiry'].tzinfo.localize(eqdata.index[0]):
                raise UnfinalizedPrice
            _finalize(eqdata, opt)
            return True
        raise

def _finalize(eqdata, opt):
    stock_price = eqdata.loc[opt['Expiry'].replace(tzinfo=None, hour=0)]['Close']
    opt['Price'] = optutils.get_parity(stock_price, opt['Opt_Type'], opt['Strike'])
    opt['Final_Price'] = True

def _get_earliest(opts, earliest=None):
    for opt in opts:
        if not earliest or opt['Expiry'] < earliest:
            earliest = opt['Expiry']
    return earliest
