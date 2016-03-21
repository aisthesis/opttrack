"""
Copyright (c) 2016 Marshall Farrier
license http://opensource.org/licenses/MIT

Search for spreads satisfying certain criteria.
"""

from functools import partial

import pytz

from lib.dbwrapper import job
from lib.logutil import getlogger
from lib.ui.find_menu import FindMenu

SERVICE_NAME = 'find'

class Find(object):

    def __init__(self):
        self.logger = getlogger(SERVICE_NAME)
        self.logger.debug('logger created')
        self.menu = FindMenu(self.logger)

    def start(self):
        while self.menu.run('main'):
            pass

if __name__ == '__main__':
    Find().start()
