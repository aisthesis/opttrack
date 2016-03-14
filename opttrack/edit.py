"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Interactively start and stop tracking an option.
"""

from bson.codec_options import CodecOptions
import datetime as dt
from functools import partial

from pymongo.errors import BulkWriteError
import pytz

from lib import config
from lib import constants
from lib.dbtools import create_index, getcoll
from lib.dbwrapper import job
from lib.logutil import getlogger

SERVICE_NAME = 'edit'

class Menu(object):

    def __init__(self):
        self.actions = {
                'main': {
                    '0': lambda: False,
                    '1': self._track_single,
                    '2': self._spread_menu,
                    '3': self._stop_track,
                    '4': self._show_tracked,
                    },
                'spread': {
                    '0': lambda: True,
                    '1': self._track_dgb,
                    },
                }
        self.tz = pytz.timezone('US/Eastern')
        self.logger = getlogger(SERVICE_NAME)
        self.logger.debug('logger created')

    def start(self):
        # ensure unique index on 'track' collection
        job(self.logger, partial(create_index, 'track'))
        proceed = True
        while proceed:
            print('\nMain menu:')
            print('1. Start tracking single option')
            print('2. Start tracking spread')
            print('3. Stop tracking single option')
            print('4. Show tracked')
            print('\n0. Quit')
            choice = input('\nEnter selection: ')
            proceed = self._exec_menu('main', choice)
        
    def _exec_menu(self, name, choice):
        try:
            return self.actions[name][choice.strip()]()
        except KeyError:
            print('Invalid selection')
            return True

    def _spread_menu(self):
        print('\nSelect spread:')
        print('1. Diagonal butterfly')
        print('\n0. Return to main menu')
        choice = input('\nEnter selection: ')
        return self._exec_menu('spread', choice)

    def _single_menu(self):
        entry = {}
        entry['Underlying'] = input('Underlying equity: ').strip().upper()
        entry['Opt_Type'] = _getopttype(input('Option type (c[all] or p[ut]): '))
        entry['Expiry'] = self._getexpdt(input('Expiration (yyyy-mm-dd): '))
        entry['Strike'] = float(input('Strike: '))
        return entry

    def _show_tracked(self):
        underlying = input('Underlying equity: ').strip().upper()
        job(self.logger, partial(_show_all_fromdb, self.tz, underlying))
        return True

    def _track_single(self):
        entries = (self._single_menu(),)
        self._confirmsave(entries)
        return True

    def _stop_track(self):
        entry = self._single_menu()
        self._confirmdelete(entry)
        return True

    def _track_dgb(self):
        print('\nTrack diagonal butterfly:')
        underlying = input('Underlying equity: ').strip().upper()
        straddleexp = self._getexpdt(input('Straddle expiration (yyyy-mm-dd): '))
        straddlestrike = float(input('Straddle strike: '))
        farexp = self._getexpdt(input('Far expiration (yyyy-mm-dd): '))
        distance = float(input('Distance between strikes: '))
        entries = _get_dgbentries(underlying, straddleexp, straddlestrike, farexp, distance)
        self._confirmsave(entries)
        return True

    def _getexpdt(self, expstr):
        # on 2016-02-19 expired options were unavailable on yahoo by 7:30 pm EST
        return self.tz.localize(dt.datetime.strptime(expstr, '%Y-%m-%d')).replace(hour=19)

    def _confirmsave(self, entries):
        print('\nSaving the following options:')
        _showentries(entries)
        choice = input('\nOK to proceed (y/n)? ').lower()
        if choice == 'y':
            job(self.logger, partial(_saveentries, entries))
        else:
            print('Aborting: option(s) NOT saved!')

    def _confirmdelete(self, entry):
        print('\nDeleting the following option:')
        _showentry(entry)
        choice = input('\nStop tracking this option (y/n)? ').lower()
        if choice == 'y':
            job(self.logger, partial(_delentry, entry))
        else:
            print('Aborting: option NOT deleted!')

def _get_dgbentries(underlying, straddleexp, straddlestrike, farexp, distance):
    entries = []
    farstrikes = {'call': straddlestrike + distance, 'put': straddlestrike - distance}
    for key in farstrikes:
        # straddle
        entries.append({'Underlying': underlying, 'Opt_Type': key, 'Expiry': straddleexp,
            'Strike': straddlestrike})
        # long-term spread
        entries.append({'Underlying': underlying, 'Opt_Type': key, 'Expiry': farexp,
            'Strike': farstrikes[key]})
    return entries

def _show_all_fromdb(tz, underlying, logger, client):
    c_opts = CodecOptions(tz_aware=True)
    trackcoll = getcoll(client, 'track', codec_options=c_opts)
    print('\nEntries for {}:\n'.format(underlying))
    for entry in trackcoll.find({'Underlying': underlying}):
        _show_foreq_fromdb(tz, entry)

def _show_foreq_fromdb(tz, entry):
    print('Opt_Type: {}'.format(entry['Opt_Type']))
    print('Expiry: {}'.format(entry['Expiry'].astimezone(tz).strftime('%Y-%m-%d')))
    print('Strike: {:.2f}\n'.format(entry['Strike']))

def _delentry(entry, logger, client):
    logger.info('removing 1 option from track collection')
    logger.debug('deleting: {}'.format(entry))
    trackcoll = getcoll(client, 'track')
    result = trackcoll.delete_many(entry)
    n_deleted = result.deleted_count
    if n_deleted > 0:
        msg = '{} record deleted'.format(n_deleted)
        print(msg)
        logger.info(msg)
    else:
        print('\nNo matching entry found. Record was NOT deleted.\n')
        logger.warn('Record not found: {}'.format(entry))

def _saveentries(entries, logger, client):
    msg = 'Saving {} entries'.format(len(entries))
    print(msg)
    logger.info(msg)
    trackcoll = getcoll(client, 'track')
    bulk = trackcoll.initialize_unordered_bulk_op()
    for entry in entries:
        bulk.insert(entry)
        logger.debug('{} queued for insertion'.format(entry))
    try:
        result = bulk.execute()
    except BulkWriteError:
        logger.exception("error writing to database")
        print('\nERROR writing to database! Entries not saved!')
        print('Are you trying to enter a duplicate record?')
    else:
        msg = '{} records saved'.format(result['nInserted'])
        print(msg)
        logger.info(msg)

def _showentries(entries):
    for entry in entries:
        print('')
        _showentry(entry)

def _getopttype(selection):
    if selection.strip().lower() in ('c', 'call'):
        return 'call'
    if selection.strip().lower() in ('p', 'put'):
        return 'put'
    raise ValueError('option type must be call or put')

def _showentry(entry):
    print('Underlying: {}'.format(entry['Underlying']))
    print('Opt_Type: {}'.format(entry['Opt_Type']))
    print('Expiry: {}'.format(entry['Expiry'].strftime('%Y-%m-%d')))
    print('Strike: {:.2f}'.format(entry['Strike']))

if __name__ == '__main__':
    Menu().start()
