"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Get options data from mongo.

The idea here is to pull historical options data from mongo
for purposes of charting the behavior of spreads against stock
prices.

Initial spec: Put pulled data into a DataFrame with the obvious
TimeSeries (quote time) as index and columns describing the option,
such as (32.0, dt.datetime(2016, 6, 18), 'call'). The content
would then be price.
"""

class QuotePuller(object):

    pass
