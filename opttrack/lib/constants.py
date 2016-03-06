"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Constants for working with an options database
"""

LOG = {
        'format': "%(asctime)s %(levelname)s %(module)s.%(funcName)s : %(message)s",
        'path': 'opttrack',
        }

DB = {
        'dev': {
            'name': 'test'
            },
        'prod': {
            'name': 'optMkt'
            }
        }

INT_COLS = ('Vol', 'Open_Int',)
FLOAT_COLS = ('Last', 'Bid', 'Ask',)

MAX_RETRIES = {
        'dev': 2,
        'prod': 4,
        }
