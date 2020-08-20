import os
import subprocess
import sys
import threading
from datetime import datetime

from database import BdsLogger
from database.ConfigHelper import get_config
from database.database import bds_log
from utils.bds_filter import BdsFilter
from utils.ws_utils import WebSocketCollector


class BdsCore:

    need_log = True

    def __init__(self, ws_collector: WebSocketCollector, no_bds=False):
        self.ws_collector = ws_collector
        self.log_filter = BdsFilter()
        if no_bds:
            self.script = ''
            self.shell = True
        else:
            if 'linux' in sys.platform:
                self.script = 'cd %s \n %s' % (
                    get_config('bedrock_server_root'),
                    get_config('bedrock_server_script')
                )
                self.shell = True
            elif 'win' in sys.platform:
                os.chdir(os.path.join(os.getcwd(), get_config('bedrock_server_root')))
                self.script = os.path.join(
                    os.getcwd(),
                    get_config('bedrock_server_script')
                )
                self.shell = False
        self.bds = subprocess.Popen(
            self.script,
            shell=self.shell,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8'
        )
        # Keep the `save_log` running
        self.logger = threading.Thread(target=self.save_log)
        self.logger.start()

    # noinspection PyMethodMayBeStatic
    def on_stopped(self):
        self.ws_collector.sent_to_all('bds', 'stopping', status=self.if_alive())
        BdsLogger.put_log('subprocess', 'stopped')
        print('>Server Stopped')
        print('>Bedrock Server stopped. Press Ctrl+C to exit.')
        print('Enter \'restart\' to restart Manager.')
        self.need_log = False

    def bds_restart(self):
        print('>restarting...')
        self.ws_collector.sent_to_all('bds', 'restart', status=self.if_alive())
        BdsLogger.put_log('bds', 'restart')
        if self.if_alive():
            self.bds.stdin.write('stop\n')
            self.bds.stdin.flush()
        while self.if_alive():
            continue
        del self.bds
        self.bds = subprocess.Popen(
            self.script,
            shell=self.shell,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8'
        )
        # Keep the `save_log` running
        self.need_log = True
        self.logger = threading.Thread(target=self.save_log)
        self.logger.start()

    def if_alive(self):
        if subprocess.Popen.poll(self.bds) is None:
            return True
        else:
            return False

    # Save the logs from bds to db
    def save_log(self):
        # noinspection PyUnresolvedReferences
        for line in iter(self.bds.stdout.readline, b''):
            if self.need_log is False:
                return
            if self.bds is None:
                continue
            if not self.if_alive():
                self.on_stopped()
            if line != '':
                line = line.replace('\n', '')
                log_type = self.log_filter.sort_log(line)
                if_ignore = self.log_filter.if_ignore(line)
                self.ws_collector.sent_to_all(log_type, line, ignore=if_ignore)
                BdsLogger.put_log(log_type, line, ignore=if_ignore)

    # Send commend to bds and get result
    # noinspection PyUnboundLocalVariable
    def cmd_in(self, cmd: str, ignore=False):
        self.ws_collector.sent_to_all('cmd_in', cmd, status=self.if_alive(), ignore=ignore)
        BdsLogger.put_log('cmd_in', cmd, ignore=ignore)
        if cmd == 'restart':
            self.bds_restart()
            return
        in_time = datetime.now()
        _log = bds_log(time=in_time, log_type='bds', log='Null')
        if not self.if_alive():
            return _log
        print('>>', cmd)
        self.bds.stdin.write(cmd + '\n')
        self.bds.stdin.flush()
