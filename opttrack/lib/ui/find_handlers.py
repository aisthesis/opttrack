"""
Copyright (c) 2015 Marshall Farrier
license http://opensource.org/licenses/MIT

lib/ui/handlers.py

Handlers for find menu
"""

from functools import partial
import sys
import traceback

import pynance as pn

from ..dbtools import find_job
from ..dbwrapper import job
from ..spreads.diagonal_butterfly import DiagonalButterfly
from .. import strikes

class FindHandlers(object):

    def __init__(self, logger):
        self.logger = logger

    def get_dgbs(self):
        """
        Scan a list of equities for potential diagonal butterfly spreads.

        For the type of equity to examine cf. McMillan, p. 344:
        'one would like the underlying stock to be somewhat volatile,
        since there is the possibility that long-term options will
        be owned for free'.

        The selection logic can be found in lib.spreads.diagonal_butterfly.DiagonalButterfly
        """
        cursor = job(self.logger, partial(find_job, 'find', {'spread': 'dgb'}))
        equities = sorted([item['eq'] for item in cursor])
        dgbs = self._find_dgbs(equities)
        _show_dgbs(dgbs)
        return True

    def _find_dgbs(self, equities):
        print('scanning {} equities for diagonal butterfly spreads'.format(len(equities)))
        dgbs = []
        for equity in equities:
            print('{}'.format(equity), end='')
            try:
                dgbs_foreq = _find_dgbs_foreq(equity)
                dgbs.extend(dgbs_foreq)
                print('({}).'.format(len(dgbs_foreq)), end='')
            except AttributeError:
                print('({}).'.format('ERROR'), end='')
                self.logger.exception('error retrieving options data')
            except Exception:
                traceback.print_exc()
                self.logger.exception('error retrieving options data')
            finally:
                sys.stdout.flush()
        return dgbs

def _find_dgbs_foreq(equity):
    opts = pn.opt.get(equity)
    return DiagonalButterfly(opts).get()

def _show_dgbs(dgbs):
    pass

def _show_dgb(dgb):
    pass
