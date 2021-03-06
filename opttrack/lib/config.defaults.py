"""
.. Copyright (c) 2016 Marshall Farrier
   license http://opensource.org/licenses/MIT

Example configurations

Copy this file to `config.py` and make changes there
as appropriate for your system.
"""

ENV = 'dev'
# OS X
# LOG_ROOT = '/usr/local/var/log'
# Ubuntu
LOG_ROOT = '/var/log/opttrack'
MONGO_CLIENT = {
        'host': '127.0.0.1',
        'port': 27017,
        'ssl': True,
        'ssl_certfile': '/home/opttrack/.ssl/client.pem',
        'ssl_ca_certs': '/home/opttrack/.ssl/ca.pem',
        'ssl_match_hostname': False,
        }
