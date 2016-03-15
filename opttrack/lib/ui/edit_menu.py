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
                        {   'desc': 'Start tracking single option',
                            'do': self.handlers.track_single},
                        {   'desc': 'Start tracking spread',
                            'do': partial(self.run, 'spread')},
                        {   'desc': 'Stop tracking single option',
                            'do': self.handlers.delete_tracked},
                        {   'desc': 'Show tracked',
                            'do': self.handlers.show_tracked},
                        ]},
                'spread': {
                    'title': 'Select spread',
                    'choices': [
                        {   'desc': 'Return to main menu',
                            'do': lambda: True},
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
