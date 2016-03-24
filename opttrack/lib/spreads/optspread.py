"""
./opttrack/lib/optspread.py

Copyright (c) 2016 Marshall Farrier
license http://opensource.org/licenses/MIT

Generic spread class
"""

SPREAD_TYPES = (
        'dgb',
        'dblcal',)

class OptSpread(object):

    def __init__(self, equity=None, spread_type=None, ref_price=None, **kwargs):
        # unconventional capitalization allows use of built-in
        # `vars()` to create a dictionary with correct keys.
        if equity:
            assert spread_type in SPREAD_TYPES
            self.Underlying = equity.upper()
            self.Spread_Type = spread_type
            self.Ref_Price = float(ref_price)
        else:
            for key in kwargs:
                setattr(self, key, kwargs[key])
        self.Long = []
        self.Short = []

