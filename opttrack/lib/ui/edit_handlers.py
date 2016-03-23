"""
Copyright (c) 2015 Marshall Farrier
license http://opensource.org/licenses/MIT

lib/ui/handlers.py

Handlers for edit menu
"""

from bson.codec_options import CodecOptions
import datetime as dt
from functools import partial

from pymongo.errors import BulkWriteError

from ..dbschema import SPREADS
from ..dbtools import delete_many, find_job, getcoll, insert_many
from ..dbwrapper import job

class EditHandlers(object):

    def __init__(self, logger, tz):
        self.logger = logger
        self.tz = tz

    def add_find(self, spread_type):
        if _is_fromfile():
            fname = input('Enter file name: ').strip()
            equities = _eqs_fromfile(fname)
        else:
            equities = _eqs_fromblob(input('Underlying equities (GOOGL,TSLA,FB): '))
        print('Include in future scans:\n')
        for eq in equities:
            print("'{}'".format(eq))
        choice = input('\nOK to proceed (y/n)? ').lower()
        if choice == 'y':
            entries = _get_find_entries(equities, spread_type)
            job(self.logger, partial(_saveentries, entries, 'find'))
        else:
            print('Aborting: equities NOT saved!')
        return True

    def del_find(self, spread_type):
        equities = _eqs_fromblob(input('Underlying equities (GOOGL,TSLA,FB): '))
        print('Remove from future scans:\n')
        for eq in equities:
            print("'{}'".format(eq))
        choice = input('\nOK to proceed (y/n)? ').lower()
        if choice == 'y':
            entries = _get_find_entries(equities, spread_type)
            job(self.logger, partial(_delentries, entries, 'find'))
        else:
            print('Aborting: equities NOT deleted!')
        return True

    def show_find(self):
        for spread in SPREADS:
            cursor = job(self.logger, partial(find_job, 'find', {'spread': spread['key']}))
            equities = sorted([item['eq'] for item in cursor])
            print('\n{}:'.format(spread['desc']))
            if len(equities) > 0:
                print('{} equities are being scanned'.format(len(equities)))
                for equity in equities:
                    print("'{}'".format(equity))
            else:
                print('No equities are being scanned')
        return True

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
            job(self.logger, partial(_saveentries, entries, 'track'))
        else:
            print('Aborting: option(s) NOT saved!')

    def _confirmdelete(self, entry):
        print('\nDeleting the following option:')
        _show_track_entries((entry,))
        choice = input('\nStop tracking this option (y/n)? ').lower()
        if choice == 'y':
            job(self.logger, partial(_delentries, (entry,), 'track'))
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

def _delentries(entries, collname, logger, client):
    logger.info("removing {} option(s) from collection '{}'".format(len(entries), collname))
    coll = getcoll(client, collname)
    total_deleted = 0
    for entry in entries:
        n_deleted = delete_many(logger, coll, entry)
        if n_deleted < 1:
            logger.warn('entry to be deleted not found: {}'.format(entry))
        total_deleted += n_deleted
    if total_deleted == len(entries):
        msg = '{} record(s) deleted'.format(total_deleted)
        print(msg)
    else:
        msg = '{} entries to be deleted but {} records deleted!'.format(len(entries), total_deleted)
        logger.warn(msg)
        print('WARNING: {}'.format(msg))
        print('Did you verify that the records to be deleted were actually present?')

def _saveentries(entries, collname, logger, client):
    msg = 'Saving {} entries'.format(len(entries))
    print(msg)
    logger.info(msg)
    coll = getcoll(client, collname)
    try:
        n_inserted = insert_many(logger, coll, entries)
    except BulkWriteError:
        print('\nERROR writing to database! Entries not saved!')
        print('Are you trying to enter duplicate records?')
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

def _is_fromfile():
    if input('Get list from file, 1 equity per line (y/n)? ').strip().lower() == 'y':
        return True
    return False

def _eqs_fromblob(eqblob):
    return sorted(map(_fmt_eq, eqblob.split(',')))

def _fmt_eq(rawtxt):
    return rawtxt.strip().upper()

def _eqs_fromfile(fname):
    equities = []
    with open(fname, 'r') as infile:
        equities = infile.readlines()
    return sorted(map(_fmt_eq, equities))

def _get_find_entries(equities, spread_type):
    return [{'eq': equity, 'spread': spread_type} for equity in equities]

