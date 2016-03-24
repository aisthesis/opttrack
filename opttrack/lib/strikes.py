"""
./opttrack/lib/strikes.py

Copyright (c) 2016 Marshall Farrier
license http://opensource.org/licenses/MIT

Utilities for finding strike prices
"""

def closest(allstrikes, eqprice):
    for i in range(len(allstrikes)):
        if allstrikes[i] >= eqprice:
            if i == 0 or allstrikes[i] - eqprice < eqprice - allstrikes[i - 1]:
                return [allstrikes[i]]
            if allstrikes[i] - eqprice == eqprice - allstrikes[i - 1]:
                return [allstrikes[i - 1], allstrikes[i]]
            return [allstrikes[i - 1]]
    if allstrikes:
        return [allstrikes[-1]]
    return []

def allforexp(opts, exp, opttype):
    strikeprices = opts.data.xs((exp, opttype), level=('Expiry', 'Type')).index.get_level_values(0)
    return list(map(_forcetofloat, strikeprices))

def matchedforexp(opts, exp):
    return _matching(allforexp(opts, exp, 'call'), allforexp(opts, exp, 'put'))

def getlastmatched(strike_to_match, strikeprices, endix, epsilon=.01):
    """
    Return the index of the last item in a sorted list of
    strikeprices that matches strike_to_match. Search descending from endix
    in the list of strikeprices.
    A match is defined as a strike differing from strike_to_match
    by less than epsilon.
    Return -1 if no match is found.
    """
    while endix >= 0:
        if abs(strike_to_match - strikeprices[endix]) < epsilon:
            return endix
        if strikeprices[endix] < strike_to_match:
            return -1
        endix -= 1
    return -1

def _forcetofloat(val):
    try:
        return float(val)
    except ValueError:
        # strings with commas are the concern, e.g. '1,040.00'
        return float(val.replace(',', ''))

def _matching(callstrikes, putstrikes):
    icall = -1
    iput = -1
    matching = []
    ncallstrikes = len(callstrikes)
    nputstrikes = len(putstrikes)
    while True:
        icall, iput = _nextsynchronized(callstrikes, putstrikes, icall, iput, ncallstrikes, nputstrikes)
        if icall < ncallstrikes:
            matching.append(callstrikes[icall])
        else:
            return matching
    
def _nextsynchronized(callstrikes, putstrikes, icall, iput, ncallstrikes, nputstrikes):
    nxt_icall = icall + 1
    nxt_iput = iput + 1
    if nxt_icall >= ncallstrikes or nxt_iput >= nputstrikes:
        return ncallstrikes, nputstrikes
    while callstrikes[nxt_icall] < putstrikes[nxt_iput]:
        nxt_icall += 1
        if nxt_icall >= ncallstrikes:
            return ncallstrikes, nputstrikes
    while putstrikes[nxt_iput] < callstrikes[nxt_icall]:
        nxt_iput += 1
        if nxt_iput >= nputstrikes:
            return ncallstrikes, nputstrikes
    return nxt_icall, nxt_iput
