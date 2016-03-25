"""
Copyright (c) 2016 Marshall Farrier
license http://opensource.org/licenses/MIT

lib/ui/utils.py

Utility functions for UIs.
"""

def confirm():
    choice = input('OK to proceed (y/n)? ').lower()
    if choice == 'y':
        return True
    return False
