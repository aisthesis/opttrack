"""
Copyright (c) 2015 Marshall Farrier
license http://opensource.org/licenses/MIT

lib/ui/edit_menu.py

Content for interactive editor
"""

from functools import partial

from .edit_handlers import EditHandlers
from .menu import Menu
from .spread_selector import SpreadSelector

class EditMenu(Menu):

    def __init__(self, logger, tz):
        super(EditMenu, self).__init__(logger, tz=tz)
        self.spread_sel = SpreadSelector()
        self._handlers = EditHandlers(self.logger, self.tz)
        self._menus = {
                'main': {
                    'title': 'Main menu',
                    'choices': [
                        {   'desc': 'Quit',
                            'do': lambda: False},
                        {   'desc': 'Find (scan for trades)',
                            'do': partial(self.run, 'find')},
                        {   'desc': 'Observe (current watch list)',
                            'do': partial(self.run, 'observe')},
                        {   'desc': 'Track (save daily)',
                            'do': partial(self.run, 'track')},
                        ]},
                'find': {
                    'title': 'Find (scan for trades)',
                    'choices': [
                        {   'desc': 'Return to main menu',
                            'do': lambda: True},
                        {   'desc': 'Add to scan list',
                            'do': partial(self.run, 'add_find')},
                        {   'desc': 'Remove from scan list',
                            'do': partial(self.run, 'del_find')},
                        {   'desc': 'Show scanned',
                            'do': self.handlers.show_find},
                        ]},
                'observe': {
                    'title': 'Observe (edit watch list)',
                    'choices': [
                        {   'desc': 'Return to main menu',
                            'do': lambda: True},
                        {   'desc': 'Start observing',
                            'do': partial(self.run, 'add_obs')},
                        {   'desc': 'Stop observing',
                            'do': partial(self.run, 'del_obs')},
                        {   'desc': 'Show observed',
                            'do': partial(self.run, 'show_obs')},
                        ]},
                'track': {
                    'title': 'Track menu',
                    'choices': [
                        {   'desc': 'Return to main menu',
                            'do': lambda: True},
                        {   'desc': 'Start tracking',
                            'do': partial(self.run, 'track_spread')},
                        {   'desc': 'Stop tracking',
                            'do': self.handlers.delete_tracked},
                        {   'desc': 'Show tracked',
                            'do': self.handlers.show_tracked},
                        ]},
                'add_find': self.spread_sel.get(dgb=partial(self.handlers.add_find, 'dgb')), 
                'del_find': self.spread_sel.get(dgb=partial(self.handlers.del_find, 'dgb')),
                'add_obs': self.spread_sel.get(dgb=partial(self.handlers.add_obs, 'dgb')), 
                'del_obs': self.spread_sel.get(dgb=partial(self.handlers.del_obs, 'dgb')), 
                'show_obs': self.spread_sel.get(dgb=partial(self.handlers.show_obs, 'dgb')), 
                'track_spread': {
                    'title': 'Track spread',
                    'choices': [
                        {   'desc': 'Return to main menu',
                            'do': lambda: True},
                        {   'desc': 'Track single option',
                            'do': self.handlers.track_single},
                        {   'desc': 'Track diagonal butterfly',
                            'do': self.handlers.track_dgb},
                        ]},
                }

    @property
    def menus(self):
        return self._menus
        
    @property
    def handlers(self):
        return self._handlers
