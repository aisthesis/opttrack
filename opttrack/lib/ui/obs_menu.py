"""
Copyright (c) 2015 Marshall Farrier
license http://opensource.org/licenses/MIT

lib/ui/edit_menu.py

Content for interactive editor
"""

from functools import partial

from .obs_handlers import ObsHandlers
from .menu import Menu
from .spread_selector import SpreadSelector

class ObsMenu(Menu):

    def __init__(self, logger, tz):
        super(ObsMenu, self).__init__(logger, tz=tz)
        self.spread_sel = SpreadSelector()
        self._handlers = ObsHandlers(self.logger, self.tz)
        overrides = {'main': {'desc': 'Quit', 'do': lambda: False}}
        self._menus = {'main': self.spread_sel.get(overrides, 
                dgb=partial(self.handlers.obs, 'dgb'))}

    @property
    def menus(self):
        return self._menus
        
    @property
    def handlers(self):
        return self._handlers
