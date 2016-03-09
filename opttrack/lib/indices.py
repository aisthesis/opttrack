"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

MongoDB indices
"""

from pymongo import ASCENDING

COLLS = {
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
        'watchList': {
            'keys': [
                ('eq', ASCENDING),
                ('spread', ASCENDING),
                ],
            'unique': True,
            },
        }
