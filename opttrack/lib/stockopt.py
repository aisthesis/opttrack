"""
./opttrack/lib/stockopt.py

Copyright (c) 2016 Marshall Farrier
license http://opensource.org/licenses/MIT

Create uniformly structured stock options objects.

Enforces correct option formation.
The `expiry` field may be a string of the form '2016-01-01',
a timezone naive datetime object (for which it is assumed
that minute, second and microsecond are all 0), or a timezone
aware object, which is then used directly as the 'Expiry'
value of the option created.

Other keys, such as 'Underlying', 'Price', etc., can be added
subsequently as needed.
"""

import datetime as dt

import pytz
import six

class StockOptFactory(object):

    def __init__(self, tz=None):
        self.tz = tz if tz else pytz.timezone('US/Eastern')
        self.opttypes = ('call', 'put')

    def make(self, strike=None, expiry=None, opttype=None, price=None, underlying=None, **kwargs):
        """
        Creates a well-formed option dictionary from positional parameters, if provided,
        or from keyword arguments.

        If positional arguments are provided, then the following are required:
            strike
            expiry
            opttype

        Some basic validation of inputs is used in creating
        a dictionary such as:
        {   'Strike': 13.0,
            'Opt_Type': 'call',
            'Expiry': datetime.datetime(2015, 6, 7, 19, 0, tzinfo=<DstTzInfo 'US/Eastern' EDT-1 day, 20:00:00 DST>)}
        """
        if strike:
            assert opttype in self.opttypes 
            opt = {'Strike': float(strike), 
                    'Opt_Type': opttype}
            if isinstance(expiry, six.string_types):
                opt['Expiry'] = self.tz.localize(dt.datetime.strptime(expiry, '%Y-%m-%d')).replace(hour=19)
            elif expiry.tzinfo is None:
                opt['Expiry'] = self.tz.localize(expiry).replace(hour=19)
            else:
                opt['Expiry'] = expiry.astimezone(self.tz)
            opt['Underlying'] = underlying
            opt['Price'] = price or 0.
            return opt
        opt = {}
        for key in kwargs:
            opt[key] = kwargs[key]
        if opt['Expiry'].tzinfo is None:
            opt['Expiry'] = self.tz.localize(opt['Expiry']).replace(hour=19)
        else:
            opt['Expiry'] = opt['Expiry'].astimezone(self.tz)
        if 'Price' not in opt or opt['Price'] is None:
            opt['Price'] = 0.
        return opt

def get_repr(opt, show_price=True):
    price_txt = ': {:.2f}'.format(opt['Price']) if show_price else ''
    return 'Strike {:.2f} {} expiring {}{}'.format(opt['Strike'], opt['Opt_Type'], 
            opt['Expiry'].strftime('%Y-%m-%d'), price_txt)
