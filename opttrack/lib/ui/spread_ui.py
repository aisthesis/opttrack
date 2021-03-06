"""
Copyright (c) 2015 Marshall Farrier
license http://opensource.org/licenses/MIT

lib/ui/spread_ui.py

Interactively enter spreads
"""

from ..stockopt import StockOptFactory
from ..spreads.optspread import OptSpread
from .utils import confirm

class SpreadUi(object):

    def __init__(self):
        self.opt_factory = StockOptFactory()

    def get(self, spread_type):
        return {
                'dgb': self._get_dgb,
                }[spread_type]()

    def _get_dgb(self):
        underlying = input('Underlying: ').upper()
        ref_price = -float(input('Spread initial credit: '))
        spread = OptSpread(underlying, 'dgb', ref_price=ref_price)
        strike = float(input('Straddle strike: '))
        expiry = input('Straddle expiry (yyyy-mm-dd): ').strip()
        for opt_type in ('call', 'put',):
            spread.sell_one(self.opt_factory.make(strike, expiry, opt_type, underlying=underlying))
        strikes = {}
        strikes['call'] = float(input('Strangle call strike: '))
        strikes['put'] = float(input('Strangle put strike: '))
        expiry = input('Strangle expiry (yyyy-mm-dd): ').strip()
        for opt_type in ('call', 'put',):
            spread.buy_one(self.opt_factory.make(strikes[opt_type], expiry, opt_type, underlying=underlying))
        print('\nYou entered the following spread:')
        _show_dgb(spread)
        if confirm():
            return spread
        return None

def _show_dgb(spread):
    print('Underlying: {}'.format(spread.Underlying))
    print('Credit: {:.2f}'.format(-spread.Ref_Price))
    print('Short:')
    for opt in spread.Short:
        _show_dgb_opt(opt, '  ')
    print('Long:')
    for opt in spread.Long:
        _show_dgb_opt(opt, '  ')

def _show_dgb_opt(opt, indent=''):
    print('{}Strike {:.2f} {} expiring on {}'.format(indent, opt['Strike'], opt['Opt_Type'],
            opt['Expiry'].strftime('%Y-%m-%d')))
