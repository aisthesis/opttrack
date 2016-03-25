"""
./opttrack/lib/optspread.py

Copyright (c) 2016 Marshall Farrier
license http://opensource.org/licenses/MIT

Generic spread class
"""

from functools import reduce

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

    def price(self):
        short_sum = reduce(_add_opt_prices, self.Short, 0.)
        return reduce(_add_opt_prices, self.Long, -short_sum)

    def buy_one(self, opt):
        self.Long.append(opt)

    def sell_one(self, opt):
        self.Short.append(opt)

    def buy_many(self, opts):
        self.Long.extend(opts)

    def sell_many(self, opts):
        self.Short.extend(opts)

    def show(self):
        print(vars(self))

def _add_opt_prices(opt1, opt2):
    return opt1['Price'] + opt2['Price']

