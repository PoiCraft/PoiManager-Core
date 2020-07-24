import signal
import sys

from auth.Token import TokenManager
from core.bds import BdsCore
from core.core import ManagerCore
from database import BdsLogger
from database.ConfigHelper import get_config
from loader.PropertiesLoader import PropertiesLoader


# noinspection PyUnusedLocal
def CtrlC(*args):
    print('>stopped<')
    BdsLogger.put_log('manager', 'stop_done')
    sys.exit()


# noinspection PyTypeChecker
signal.signal(signal.SIGINT, CtrlC)
# noinspection PyTypeChecker
signal.signal(signal.SIGTERM, CtrlC)

if __name__ == '__main__':

    argv = sys.argv
    debug = False
    if len(argv) > 1:
        if argv[1] == 'debug':
            debug = True

    if debug:
        print('>Manager Debug')

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

    prop_loader = PropertiesLoader()
    bdsCore = BdsCore()

    if get_config('clear_log_on_start') == 'true':
        BdsLogger.clear_log()

    managerCore = ManagerCore(token_manager=tokenManager,
                              bds=bdsCore,
                              prop_loader=prop_loader,
                              name=__name__,
                              debug=debug)
    managerCore.run()
