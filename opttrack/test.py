from lib import constants
from lib.indices import COLLS 

def show(keys, unique, background):
    print(keys)
    print(unique)
    print(background)

if __name__ == '__main__':
    show(**COLLS['watchList'], background=True)
