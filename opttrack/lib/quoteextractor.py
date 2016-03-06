"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Extract specific quotes from a comprehensive DataFrame

Example entry:
    {
    'Underlying': 'NFLX',
    'Strike': 100.0,
    'Expiry': datetime.datetime(2016, 3, 18, 23, 0, tzinfo=<bson.tz_util.FixedOffset object at 0x10c4860b8>),
    'Opt_Type': 'put',
    'Opt_Symbol': 'NFLX160318P00100000',
    'Last': 10.25,
    'Bid': 9.7,
    'Ask': 10.05,
    'Vol': 260,
    'Open_Int': 23567,
    'Quote_Time': datetime.datetime(2016, 2, 22, 16, 0, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)
    }
"""

from . import constants

class QuoteExtractor(object):

    def __init__(self, logger, underlying, opts, tznyse):
        self.logger = logger
        self.tznyse = tznyse
        self.underlying = underlying
        self.opts = opts

    def get(self, specs):
        return self._extract_all(specs)

    def _extract_all(self, specs):
        entries = []
        self.logger.info('getting {} quote(s) for {}'.format(len(specs), self.underlying))
        for spec in specs:
            try:
                entry = self._extract_one(spec)
            except KeyError:
                continue
            else:
                entries.append(entry)
        return entries

    def _extract_one(self, spec):
        entry = spec.copy()
        selection = (spec['Strike'], spec['Expiry'].astimezone(self.tznyse).replace(tzinfo=None,
                hour=0, minute=0, second=0), spec['Opt_Type'],)
        try:
            entry['Opt_Symbol'] = self.opts.data.loc[selection, :].index[0]
            opt = self.opts.data.loc[selection, :].iloc[0]
        except KeyError as e:
            self.logger.exception('option not found for {} with {}'
                    .format(self.opts.data.iloc[0, :].loc['Underlying'], selection))
            raise
        entry['Quote_Time'] = self.tznyse.localize(opt['Quote_Time'].to_datetime())
        entry['Underlying'] = opt['Underlying']
        for key in constants.INT_COLS:
            entry[key] = int(opt[key])
        for key in constants.FLOAT_COLS:
            entry[key] = float(opt[key])
        self.logger.debug(entry)
        return entry

