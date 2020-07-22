import sys

from auth.Token import TokenManager
from core.bds import BdsCore
from database import BdsLogger
from database.ConfigHelper import get_config
import signal
from core.core import ManagerCore


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
    BdsLogger.put_log('manager', 'start')
    BdsLogger.put_log('manager', '%s:%s' % (
        get_config('web_listening_address'),
        get_config('web_listening_port')
    ))

    print('>Listening at %s:%s' % (
        get_config('web_listening_address'),
        get_config('web_listening_port')
    ))

    tokenManager = TokenManager()
    print('>Manager Token: %s' % tokenManager.token)

    bdsCore = BdsCore()
    managerCore = ManagerCore(token_manager=tokenManager, bds=bdsCore, name=__name__)
    managerCore.run()
