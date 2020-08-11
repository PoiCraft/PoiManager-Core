import json
import os
import subprocess
import sys
import threading
from datetime import datetime

# noinspection PyPackageRequirements
from geventwebsocket.websocket import WebSocket

from database import BdsLogger
from database.ConfigHelper import get_config
from database.database import bds_log
from utils.bds_filter import BdsFilter


class BdsCore:
    ws_client = {}
    ws_client_len = 0

    need_log = True

    def add_ws(self, ws: WebSocket):
        self.ws_client[self.ws_client_len] = [ws, False]
        self.ws_client_len += 1
        return self.ws_client_len - 1

    def update_ws(self, ws_id: int):
        client = self.ws_client[ws_id]
        if client[1] is False:
            to_return = 1
        else:
            to_return = 0
        client[1] = True
        self.ws_client[ws_id] = client
        return to_return

    def check_ws(self, ws_id: int):
        return self.ws_client[ws_id][1]

    def __init__(self, no_bds=False):
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
        self.sent_to_all('bds', 'stopping')
        BdsLogger.put_log('subprocess', 'stopped')
        print('>Server Stopped')
        print('>Bedrock Server stopped. Press Ctrl+C to exit.')
        print('Enter \'restart\' to restart Manager.')
        self.need_log = False

    def bds_restart(self):
        print('>restarting...')
        self.sent_to_all('bds', 'restart')
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

    def sent_to_all(self, msg_type: str, msg: str, ignore=False):
        if ignore:
            msg = '(ignore) ' + msg
        clients = self.ws_client.copy()
        for k in clients:
            if not clients[k][0].closed:
                if clients[k][1]:
                    clients[k][0].send(json.dumps(
                        {
                            'type': msg_type,
                            'msg': msg,
                            'status': self.if_alive()
                        },
                        ensure_ascii=False))
            else:
                del self.ws_client[k]

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
                self.sent_to_all(log_type, line, ignore=if_ignore)
                BdsLogger.put_log(log_type, line, ignore=if_ignore)

    # Send commend to bds and get result
    # noinspection PyUnboundLocalVariable
    def cmd_in(self, cmd: str, ignore=False):
        BdsLogger.put_log('cmd_in', cmd, ignore=ignore)
        in_time = datetime.now()
        _log = bds_log(time=in_time, log_type='bds', log='Null')
        if not self.if_alive():
            return _log
        print('>>', cmd)
        self.bds.stdin.write(cmd + '\n')
        self.bds.stdin.flush()
