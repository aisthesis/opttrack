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

    def __init__(self):
        self.tz = pytz.timezone('US/Eastern')
        self.opttypes = ('call', 'put')

    def make(self, strike, expiry, opttype):
        """
        Some basic validation of inputs is used in creating
        a dictionary such as:
        {   'Strike': 13.0,
            'Opt_Type': 'call',
            'Expiry': datetime.datetime(2015, 6, 7, 19, 0, tzinfo=<DstTzInfo 'US/Eastern' EDT-1 day, 20:00:00 DST>)}
        """
        assert opttype in self.opttypes 
        opt = {'Strike': float(strike), 
                'Opt_Type': opttype}
        if isinstance(expiry, six.string_types):
            opt['Expiry'] = self.tz.localize(dt.datetime.strptime(expiry, '%Y-%m-%d')).replace(hour=19)
        elif expiry.tzinfo is None:
            opt['Expiry'] = self.tz.localize(expiry).replace(hour=19)
        else:
            opt['Expiry'] = expiry
        return opt
