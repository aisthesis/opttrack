"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Interactively start and stop tracking an option.
"""

from functools import partial

import pytz

from lib.dbtools import create_index
from lib.dbwrapper import job
from lib.logutil import getlogger
from lib.ui.edit_menu import EditMenu

SERVICE_NAME = 'edit'

class Edit(object):

    def __init__(self):
        self.tz = pytz.timezone('US/Eastern')
        self.logger = getlogger(SERVICE_NAME)
        self.logger.debug('logger created')
        self.menu = EditMenu(self.logger, self.tz)

    def start(self):
        # ensure unique index on 'track' collection
        job(self.logger, partial(create_index, 'track'))
        while self.menu.run('main'):
            pass

if __name__ == '__main__':
    Edit().start()
