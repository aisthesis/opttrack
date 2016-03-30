"""
Copyright (c) 2015 Marshall Farrier
license http://opensource.org/licenses/MIT

lib/ui/spread_selector.py

Template for selecting spreads.
"""

from copy import deepcopy

class SpreadSelector(object):

    def __init__(self):
        self.template = {
                'title': 'Select spread type',
                'choices': [
                    {   'desc': 'Return to main menu',
                        'abbr': 'main',
                        'do': None},
                    {   'desc': 'Diagonal butterfly',
                        'abbr': 'dgb',
                        'do': None},
                    {   'desc': 'Double calendar',
                        'abbr': 'dblcal',
                        'do': None},
                    ]}

    def get(self, overrides=None, **kwargs):
        menu = deepcopy(self.template)
        for choice in menu['choices']:
            if overrides and choice['abbr'] in overrides:
                choice['desc'] = overrides[choice['abbr']]['desc']
                choice['do'] = overrides[choice['abbr']]['do']
            else:
                choice['do'] = kwargs.get(choice['abbr'], lambda: True)
        return menu
