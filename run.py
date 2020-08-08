""" The script to run PoiManager-Core.

Use ` python3 run.py` to run this.

"""

import os
import signal
import sys

from flask import Flask

from auth.Token import TokenManager
from core.bds import BdsCore
from core.core import ManagerCore
from database import BdsLogger
from database.ConfigHelper import get_config, printConfig
from loader.PropertiesLoader import PropertiesLoader


# noinspection PyUnusedLocal
from utils.init import init_db


def CtrlC(*args):
    print('>stopped<')
    BdsLogger.put_log('manager', 'stop_done')
    while True:
        sys.exit()


# noinspection PyTypeChecker
signal.signal(signal.SIGINT, CtrlC)
# noinspection PyTypeChecker
signal.signal(signal.SIGTERM, CtrlC)

if __name__ == '__main__':

    print('>PoiManager-Core starting...')

    if os.path.isfile('db.sqlite3') is not True:
        print('Database is missing, creating...')
        init_db()

    argv = sys.argv
    debug = False
    debug_no_bds = False
    if len(argv) > 1:
        if argv[1] == 'debug':
            debug = True
        elif argv[1] == 'debug-no-bds':
            debug = True
            debug_no_bds = True

    if debug:
        print('>Manager Debug')

    print('>Configs are:')
    printConfig()

    BdsLogger.put_log('manager', 'start')
    BdsLogger.put_log('manager', '%s:%s' % (
        get_config('web_listening_address'),
        get_config('web_listening_port')
    ))

    print('>Listening at %s:%s' % (
        get_config('web_listening_address'),
        get_config('web_listening_port')
    ))

    tokenManager = TokenManager(debug=debug)
    print('>Manager Token: %s' % tokenManager.token)

    app = Flask(
            __name__,
            static_url_path='/',
            static_folder='static',
            template_folder='template'
        )

    prop_loader = PropertiesLoader(no_bds=debug_no_bds)

    bdsCore = BdsCore(no_bds=debug_no_bds)

    if get_config('clear_log_on_start') == 'true':
        BdsLogger.clear_log()

    managerCore = ManagerCore(token_manager=tokenManager,
                              bds=bdsCore,
                              prop_loader=prop_loader,
                              name=__name__,
                              app=app,
                              debug=debug)
    managerCore.run()
