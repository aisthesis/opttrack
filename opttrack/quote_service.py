"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Mediator for workflow to save specific options.
"""

import datetime as dt
from functools import partial
import signal
import sys
import time

from delayqueue import *
from pandas.tseries.offsets import BDay
import pynance as pn
import pytz

from lib import config
from lib import constants
from lib.dbwrapper import job
from lib.logutil import getlogger
from lib.quoteextractor import QuoteExtractor
from lib.quotesaver import savequotes
from lib.trackpuller import TrackPuller

SERVICE_NAME = 'quote_service'

class QuoteService(object):

    def __init__(self):
        self.logger = getlogger(SERVICE_NAME)
        self.prod = config.ENV == 'prod'
        self.tznyse = pytz.timezone('US/Eastern')
        self.done_today = False
        # for auto-failing in dev
        self.counter = 0

    def start_daemon(self):
        self.logger.info('daemon starting')
        signal.signal(signal.SIGINT, self._stop_handler)
        signal.signal(signal.SIGTERM, self._stop_handler)
        if self.prod:
            self._waitfornextclose()
        while True:
            self._run_job()
            self._waitfornextclose()

    def _run_job(self):
        self.done_today = False
        trackpuller = TrackPuller(self.logger)
        totrack = trackpuller.get()
        queue = DelayQueue()
        for underlying in totrack:
            queue.put({'eq': underlying, 'specs': totrack[underlying], 'n_retries': 0})
        delay_secs = 0
        self.counter = 0
        param_key = 'prod' if self.prod else 'dev'
        max_retries = constants.MAX_RETRIES[param_key]
        while True:
            try:
                item = queue.get()
                success = self._processqitem(item)
                if not success:
                    item['n_retries'] += 1
                    if item['n_retries'] > max_retries:
                        msg = ('{} retries would exceed maximum of {}, '
                                'abandoning spec for {}').format(item['n_retries'],
                                max_retries, item['eq'])
                        self.logger.warn(msg)
                    else:
                        queue.put(item, self._waittoretry(item['n_retries']))
            except Empty:
                self.done_today = True
                self.logger.info('done for today')
                break
            except NotReady:
                delay_secs = queue.ask()
                self.logger.info('queue not ready, waiting {:.1f} seconds'.format(delay_secs))
                time.sleep(delay_secs)
        self.logger.info('finished processing queue')

    def _processqitem(self, item):
        self.counter += 1
        if not self.prod and self.counter % 3 == 0:
            self.logger.debug('auto-failing quotes for {} in dev'.format(item['eq']))
            return False
        try:
            opts = pn.opt.get(item['eq'])
        except AttributeError:
            self.logger.exception('error retrieving option data for {}'.format(item['eq']))
            return False
        except Exception:
            self.logger.exception('error retrieving option data for {}'.format(item['eq']))
            return False
        else:
            self.logger.info('successfully retrieved options data for {}'.format(item['eq']))
            quotes = QuoteExtractor(self.logger, item['eq'], opts, self.tznyse).get(item['specs'])
            self.logger.info('{} quote(s) extracted for {}'.format(len(quotes), item['eq']))
            job(self.logger, partial(savequotes, quotes))
            return True

    def _waittoretry(self, n_retries):
        if self.prod:
            return 60 * (3 ** n_retries)
        return 15

    def _waitfornextclose(self):
        seconds = 15
        if self.prod:
            seconds = self._secondsuntilnextclose()
            self.logger.info('waiting {:.2f} hours until next close'.format(seconds / 3600.))
        else:
            self.logger.info('waiting {} seconds in dev mode'.format(seconds))
        time.sleep(seconds)

    def _secondsuntilnextclose(self):
        nysenow = dt.datetime.now(tz=self.tznyse)
        if _is_bday(nysenow) and not self.done_today:
            # a few minutes after close to be safe
            todaysclose = nysenow.replace(hour=16, minute=15)
            if nysenow >= todaysclose:
                return 0
            return (todaysclose - nysenow).seconds
        nextclose = (nysenow + BDay()).replace(hour=16, minute=15)
        diff = nextclose - nysenow
        return diff.seconds + diff.days * 24 * 3600

    def _stop_handler(self, sig, frame):
        msg = ('SIGINT' if sig == signal.SIGINT else 'SIGTERM')
        self.logger.info('signal {} received. stopping'.format(msg))
        sys.exit(0)

def _is_bday(date):
    return date.day == ((date + BDay()) - BDay()).day

if __name__ == '__main__':
    QuoteService().start_daemon()
