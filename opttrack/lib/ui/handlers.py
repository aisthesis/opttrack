"""
Copyright (c) 2015 Marshall Farrier
license http://opensource.org/licenses/MIT

lib/ui/handlers.py

Handlers for menu selections.
"""

from bson.codec_options import CodecOptions
import datetime as dt
from functools import partial

from ..dbtools import delete_many, getcoll, insert_many
from ..dbwrapper import job

class Handlers(object):

    def __init__(self, logger, tz):
        self.logger = logger
        self.tz = tz

    def track_single(self):
        entry = self._get_track_entry()
        self._confirmsave((entry,))
        return True

    def track_dgb(self):
        print('\nTrack diagonal butterfly:')
        underlying = input('Underlying equity: ').strip().upper()
        straddleexp = self._getexpdt(input('Straddle expiration (yyyy-mm-dd): '))
        straddlestrike = float(input('Straddle strike: '))
        farexp = self._getexpdt(input('Far expiration (yyyy-mm-dd): '))
        distance = float(input('Distance between strikes: '))
        entries = _get_dgbentries(underlying, straddleexp, straddlestrike, farexp, distance)
        self._confirmsave(entries)
        return True

    def delete_tracked(self):
        entry = self._get_track_entry()
        self._confirmdelete(entry)
        return True

    def show_tracked(self):
        underlying = input('Underlying equity: ').strip().upper()
        job(self.logger, partial(_show_tracked, self.tz, underlying))
        return True

    def _get_track_entry(self):
        entry = {}
        entry['Underlying'] = input('Underlying equity: ').strip().upper()
        entry['Opt_Type'] = _getopttype(input('Option type (c[all] or p[ut]): '))
        entry['Expiry'] = self._getexpdt(input('Expiration (yyyy-mm-dd): '))
        entry['Strike'] = float(input('Strike: '))
        return entry

    def _confirmsave(self, entries):
        print('\nSaving the following options:')
        _show_track_entries(entries)
        choice = input('\nOK to proceed (y/n)? ').lower()
        if choice == 'y':
            job(self.logger, partial(_saveentries, entries))
        else:
            print('Aborting: option(s) NOT saved!')

    def _confirmdelete(self, entry):
        print('\nDeleting the following option:')
        _show_track_entries((entry,))
        choice = input('\nStop tracking this option (y/n)? ').lower()
        if choice == 'y':
            job(self.logger, partial(_delentry, entry))
        else:
            print('Aborting: option NOT deleted!')

    def _getexpdt(self, expirytxt):
        # on 2016-02-19 expired options were unavailable on yahoo by 7:30 pm EST
        return self.tz.localize(dt.datetime.strptime(expirytxt, '%Y-%m-%d')).replace(hour=19)
        
def _getopttype(rawtxt):
    if rawtxt.strip().lower() in ('c', 'call'):
        return 'call'
    if rawtxt.strip().lower() in ('p', 'put'):
        return 'put'
    raise ValueError('option type must be call or put')

def _show_track_entries(entries):
    for entry in entries:
        print('')
        _show_track_entry(entry)

def _show_track_entry(entry):
    print('Underlying: {}'.format(entry['Underlying']))
    print('Opt_Type: {}'.format(entry['Opt_Type']))
    print('Expiry: {}'.format(entry['Expiry'].strftime('%Y-%m-%d')))
    print('Strike: {:.2f}'.format(entry['Strike']))

def _delentry(entry, logger, client):
    logger.info('removing 1 option from track collection')
    logger.debug('deleting: {}'.format(entry))
    trackcoll = getcoll(client, 'track')
    n_deleted = delete_many(logger, trackcoll, entry)
    if n_deleted > 0:
        print('{} record(s) deleted'.format(n_deleted))
    else:
        print('\nNo matching entry found. Record was NOT deleted.\n')

def _saveentries(entries, logger, client):
    msg = 'Saving {} entries'.format(len(entries))
    print(msg)
    logger.info(msg)
    trackcoll = getcoll(client, 'track')
    try:
        n_inserted = insert_many(logger, trackcoll, entries)
    except BulkWriteError:
        print('\nERROR writing to database! Entries not saved!')
        print('Are you trying to enter a duplicate record?')
    else:
        print('{} records saved'.format(n_inserted))

def _show_tracked(tz, underlying, logger, client):
    c_opts = CodecOptions(tz_aware=True)
    trackcoll = getcoll(client, 'track', codec_options=c_opts)
    print('\nEntries for {}:\n'.format(underlying))
    for record in trackcoll.find({'Underlying': underlying}):
        _show_tracked_record(tz, record)

def _show_tracked_record(tz, record):
    print('Opt_Type: {}'.format(record['Opt_Type']))
    print('Expiry: {}'.format(record['Expiry'].astimezone(tz).strftime('%Y-%m-%d')))
    print('Strike: {:.2f}\n'.format(record['Strike']))

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
