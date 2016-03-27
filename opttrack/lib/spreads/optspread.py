"""
./opttrack/lib/optspread.py

Copyright (c) 2016 Marshall Farrier
license http://opensource.org/licenses/MIT

Generic spread class
"""

from functools import reduce

from .. import stockopt

SPREAD_TYPES = (
        'dgb',
        'dblcal',)

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

    def price(self):
        short_sum = reduce(_add_opt_prices, self.Short)
        return reduce(_add_opt_prices, self.Long) - short_sum

    def buy_one(self, opt):
        self.Long.append(opt)

    def sell_one(self, opt):
        self.Short.append(opt)

    def buy_many(self, opts):
        self.Long.extend(opts)

    def sell_many(self, opts):
        self.Short.extend(opts)

    def show(self, show_price=True, show_eq_price=True, show_metrics=True):
        stock_price_txt = ' at {:.2f}'.format(self.Underlying_Price) if show_eq_price else ''
        print('{}{}:'.format(self.Underlying, stock_price_txt))
        if show_metrics:
            self.show_metrics()
        for title in ('Long', 'Short',):
            print('{}:'.format(title))
            for opt in getattr(self, title):
                print('  {}'.format(stockopt.get_repr(opt, show_price)))

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

    def _show_dgb_metrics(self):
        metrics = self._get_dgb_metrics()
        for key in ('credit', 'risk', 'ratio',):
            print('  {}: {:.2f}'.format(key.capitalize(), metrics[key]))

    def _get_dgb_metrics(self):
        metrics = {}
        long_total = reduce(_add_opt_prices, self.Long)
        short_total = reduce(_add_opt_prices, self.Short)
        metrics['credit'] = short_total - long_total
        try:
            metrics['ratio'] = short_total / long_total
        except ZeroDivisionError:
            metrics['ratio'] = 0.
        strike_diff = abs(self.Short[0]['Strike'] - self.Long[0]['Strike'])
        metrics['risk'] = strike_diff - metrics['credit']
        return metrics

def _add_opt_prices(opt1, opt2):
    return opt1['Price'] + opt2['Price']

