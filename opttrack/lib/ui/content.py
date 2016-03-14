"""
Copyright (c) 2015 Marshall Farrier
license http://opensource.org/licenses/MIT

lib/ui/content.py

Content for interactive menus
"""

MENUS = {
        'main': [
            '\nMain menu:',
            '1. Start tracking single option',
            '2. Start tracking spread',
            '3. Stop tracking single option',
            '4. Show tracked',
            '\n0. Quit',
            ],
        'spread': [
            '\nSelect spread:',
            '1. Diagonal butterfly',
            '\n0. Return to main menu',
            ],
        }

def show_menu(menu_name):
    for row in MENUS[menu_name]:
        print(row)
