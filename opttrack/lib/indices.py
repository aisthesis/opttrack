"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

MongoDB indices
"""

COLLS = {
        'quotes': {
            'keys': ['Underlying', 'Quote_Time', 'Strike', 'Expiry', 'Opt_Type'],
            'unique': True,
            },
        'track': {
            'keys': ['Underlying', 'Strike', 'Expiry', 'Opt_Type'],
            'unique': True,
            },
        'watchList': {
            'keys': ['eq', 'spread'],
            'unique': True,
            },
        }
