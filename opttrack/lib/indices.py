"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

MongoDB indices
"""

from pymongo import ASCENDING

COLLS = {
        'find': {
            'keys': [
                ('eq', ASCENDING),
                ('spread', ASCENDING),
                ],
            'unique': True,
            },
        'observe': {
            'keys': [
                ('eq', ASCENDING),
                ('spread', ASCENDING),
                ],
#            Other expected fields:
#            'ref_price': 20.03,
#            'buy': [opt1, opt2],
#            'sell': [opt3, opt4]
            },
        'quotes': {
            'keys': [
                ('Underlying', ASCENDING),
                ('Strike',  ASCENDING),
                ('Expiry', ASCENDING),
                ('Opt_Type', ASCENDING),
                ('Quote_Time',  ASCENDING),
                ],
            'unique': True,
            },
        'track': {
            'keys': [
                ('Underlying', ASCENDING),
                ('Strike', ASCENDING),
                ('Expiry', ASCENDING),
                ('Opt_Type', ASCENDING),
                ],
            'unique': True,
            },
        }
