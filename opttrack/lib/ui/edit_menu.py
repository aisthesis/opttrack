"""
Copyright (c) 2015 Marshall Farrier
license http://opensource.org/licenses/MIT

lib/ui/edit_menu.py

Content for interactive editor
"""

from functools import partial

from .handlers import Handlers

class EditMenu(object):

    def __init__(self, logger, tz):
        self.logger = logger
        self.tz = tz
        self.handlers = Handlers(self.logger, self.tz)
        self.menus = {
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
                    'title': 'Find',
                    'choices': [
                        {   'desc': 'Return to main menu',
                            'do': lambda: True},
                        {   'desc': 'Add from console',
                            'do': lambda: True},
                        {   'desc': 'Add from file',
                            'do': lambda: True},
                        {   'desc': 'Remove from list',
                            'do': lambda: True},
                        {   'desc': 'Show scanned',
                            'do': lambda: True},
                        ]},
                'observe': {
                    'title': 'Observe (edit watch list)',
                    'choices': [
                        {   'desc': 'Return to main menu',
                            'do': lambda: True},
                        {   'desc': 'Start observing',
                            'do': lambda: True},
                        {   'desc': 'Stop observing',
                            'do': lambda: True},
                        {   'desc': 'Show observed',
                            'do': lambda: True},
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

    def run(self, menu_key):
        choice = self._show(menu_key)
        return self._do(menu_key, choice)

    def _show(self, menu_key):
        menu = self.menus[menu_key]
        choices = menu['choices']
        print('\n{}:'.format(menu['title']))
        for i in range(1, len(choices)):
            print('{}. {}'.format(i, choices[i]['desc']))
        print('\n0. {}'.format(choices[0]['desc']))
        return int(input('\nEnter selection: '))

    def _do(self, menu_key, choice):
        try:
            return self.menus[menu_key]['choices'][choice]['do']()
        except IndexError:
            print('Invalid selection')
            return True
