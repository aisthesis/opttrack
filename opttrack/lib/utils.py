"""
Copyright (c) 2016 Marshall Farrier
license http://opensource.org/licenses/MIT

lib/utils.py

General utility functions
"""

from __future__ import division

def safe_divide(numerator, denominator, default_answer=0.):
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return default_answer
