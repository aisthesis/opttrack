"""
./opttrack/observe.py

Copyright (c) 2016 Marshall Farrier
license http://opensource.org/licenses/MIT

Observe selected spreads
"""

import pytz

from lib.logutil import getlogger
from lib.ui.obs_menu import ObsMenu

SERVICE_NAME = 'observe'

class Observe(object):

    def __init__(self):
        self.logger = getlogger(SERVICE_NAME)
        self.logger.debug('logger created')
        self.tz = pytz.timezone('US/Eastern')
        self.menu = ObsMenu(self.logger, self.tz)

    def start(self):
        while self.menu.run('main'):
            pass

if __name__ == '__main__':
    Observe().start()
