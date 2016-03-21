"""
Copyright (c) 2015 Marshall Farrier
license http://opensource.org/licenses/MIT

lib/ui/handlers.py

Handlers for edit menu
"""

import pynance as pn

from ..dbwrapper import job

class FindHandlers(object):

    def __init__(self, logger):
        self.logger = logger

