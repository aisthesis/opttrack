"""
./opttrack/lib/spreads/optutils.py

Copyright (c) 2016 Marshall Farrier
license http://opensource.org/licenses/MIT

Miscellaneous utilities for working with options
"""

import locale

def get_price(opts, opt_type, strike, expiry):
    """
    This wrapper is needed because strikes with commas
    are being returned as strings by pandas-datareader
    """
    try:
        return opts.price.get(opt_type, strike, expiry)
    except KeyError:
        strikestr = locale.format("%0.2f", strike, grouping=True)
        return opts.price.get(opt_type, strikestr, expiry)
