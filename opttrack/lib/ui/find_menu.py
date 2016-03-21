"""
Copyright (c) 2015 Marshall Farrier
license http://opensource.org/licenses/MIT

lib/ui/edit_menu.py

Content for interactive find (scan)
"""

from functools import partial

from .find_handlers import FindHandlers
from .menu import Menu

class FindMenu(Menu):

    def __init__(self, logger):
        super(FindMenu, self).__init__(logger) 
        self._handlers = FindHandlers(logger)
        self._menus = {
                'main': {
                    'title': 'Select spread',
                    'choices': [
                        {   'desc': 'Quit',
                            'do': lambda: False},
                        {   'desc': 'Diagonal butterfly',
                            'do': lambda: True},
                        {   'desc': 'Double calendar (not implemented)',
                            'do': lambda: True},
                        ]},
                }

    @property
    def menus(self):
        return self._menus
        
    @property
    def handlers(self):
        return self._handlers
