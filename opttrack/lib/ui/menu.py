"""
Copyright (c) 2015 Marshall Farrier
license http://opensource.org/licenses/MIT

lib/ui/menu.py

Abstract base class for interactive menus.
"""

from abc import ABCMeta, abstractproperty

class Menu(object):

    __metaclass__ = ABCMeta

    def __init__(self, logger, **kwargs):
        self.logger = logger
        for key in kwargs:
            setattr(self, key, kwargs[key])

    @abstractproperty
    def menus(self):
        return NotImplemented

    @abstractproperty
    def handlers(self):
        return NotImplemented

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
