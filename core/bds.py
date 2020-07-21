import os
import time
import subprocess
from datetime import datetime
import threading

from gevent.pywsgi import WSGIServer

from database import BdsLogger
from database.ConfigHelper import get_config, get_session
from database.database import bds_log
import sys


class BdsCore:
    def __init__(self, server: WSGIServer):
        self.server = server
        self.bds = subprocess.Popen(
            'cd %s \n %s' % (
                get_config('bedrock_server_root'),
                get_config('bedrock_server_script')
            ),
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True
        )
        # Keep the `save_log` running
        logger = threading.Thread(target=self.save_log)
        logger.start()

    # noinspection PyMethodMayBeStatic
    def on_stopped(self):
        BdsLogger.put_log('subprocess', 'stopped')
        print('>Server Stopped')
        session = get_session()
        if session.query(bds_log).filter_by(log_type='cmd_in').all()[-1].log != 'stop':
            session.close()
            BdsLogger.put_log('subprocess', 'Unexpected stopping')
            print('>Unexpected stopping')
            BdsLogger.put_log('manager', 'restart')
            print('>restarting...')
            python = sys.executable
            os.execl(python, python, *sys.argv)
        else:
            session.close()
            print('>Manager Stopping...')
            BdsLogger.put_log('manager_core', 'stop')
            print('>Manager Core stopped. Press Ctrl+C to exit.')
            print('Enter \'restart\' to restart Manager.')
            sys.exit()

    # Save the logs from bds to db
    def save_log(self):
        for line in iter(self.bds.stdout.readline, b''):
            if subprocess.Popen.poll(self.bds) is not None:
                self.on_stopped()
            if line != '':
                line = line.replace('\n', '')
                BdsLogger.put_log('bds', line)
                print(line)

    # Send commend to bds and get result
    # noinspection PyUnboundLocalVariable
    def cmd_in(self, cmd: str) -> bds_log:
        in_time = datetime.now()
        BdsLogger.put_log('cmd_in', cmd)
        self.bds.stdin.write(cmd + '\n')
        self.bds.stdin.flush()
        _log = bds_log(time=in_time, log_type='bds', log='Null')
        for _ in range(5):
            time.sleep(0.1)
            __log = BdsLogger.get_log_all()[-1]
            if _log.time > in_time:
                _log = __log
                break
        return _log
