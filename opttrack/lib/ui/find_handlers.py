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
from ..spreads.dgb_finder import DgbFinder
from ..stockopt import StockOptFactory
from .. import strikes

class FindHandlers(object):

    def __init__(self, logger):
        self.logger = logger
        self.opt_factory = StockOptFactory()

    def get_dgbs(self):
        """
        Scan a list of equities for potential diagonal butterfly spreads.

        For the type of equity to examine cf. McMillan, p. 344:
        'one would like the underlying stock to be somewhat volatile,
        since there is the possibility that long-term options will
        be owned for free'.

        The selection logic can be found in lib.spreads.diagonal_butterfly.DgbFinder
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
                dgbs_foreq = self._find_dgbs_foreq(equity)
                dgbs.extend(dgbs_foreq)
                msg = len(dgbs_foreq)
            except AttributeError:
                msg = '?'
                self.logger.exception('error retrieving options data')
            except Exception:
                traceback.print_exc()
                self.logger.exception('error retrieving options data')
            finally:
                print('({}).'.format(msg), end='')
                sys.stdout.flush()
        return dgbs

    def _find_dgbs_foreq(self, equity):
        opts = pn.opt.get(equity)
        return DgbFinder(opts, self.opt_factory).run()

def _show_dgbs(dgbs):
    if len(dgbs) > 0:
        print('')
        for dgb in dgbs:
            print('-' * 32)
            _show_dgb(dgb)
        print('=' * 32)
    else:
        print('\nNo spreads meeting the requirements were found.')

def _show_dgb(dgb):
    print("{} at {:.2f}:".format(dgb['spread'].Underlying, dgb['spread'].Underlying_Price))
    print("Metrics:")
    print("  Credit: {:.2f}".format(dgb['metrics']['Credit']))
    print("  Risk: {:.2f}".format(dgb['metrics']['Risk']))
    print("  Ratio: {:.2f}".format(dgb['metrics']['Ratio']))
    print("Straddle with expiry {}:".format(_fmt_dt(dgb['spread'].Short[0]['Expiry'])))
    _opt = dgb['spread'].Short[0]
    print("  Strike: {:.2f} {}: {:.2f}".format(_opt['Strike'], _opt['Opt_Type'], _opt['Price']))
    _opt = dgb['spread'].Short[1]
    print("  Strike: {:.2f} {}: {:.2f}".format(_opt['Strike'], _opt['Opt_Type'], _opt['Price']))
    print("  Total: {:.2f}".format(dgb['metrics']['Near_Price'])) 
    print("Strangle with expiry {}:".format(_fmt_dt(dgb['spread'].Long[0]['Expiry'])))
    _opt = dgb['spread'].Long[0]
    print("  Strike: {:.2f} {}: {:.2f}".format(_opt['Strike'], _opt['Opt_Type'], _opt['Price']))
    _opt = dgb['spread'].Long[1]
    print("  Strike: {:.2f} {}: {:.2f}".format(_opt['Strike'], _opt['Opt_Type'], _opt['Price']))
    print("  Total: {:.2f}".format(dgb['metrics']['Far_Price']))

def _fmt_dt(expiry):
    return expiry.date()
