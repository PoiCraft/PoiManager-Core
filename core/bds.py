import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime

from geventwebsocket.websocket import WebSocket

from database import BdsLogger
from database.ConfigHelper import get_config
from database.database import bds_log


class BdsCore:

    danger_cmd = [
        'restart',
        'stop'
    ]
    ws_client = {}
    ws_client_len = 0

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

    def __init__(self):
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
        logger = threading.Thread(target=self.save_log)
        logger.start()

    # noinspection PyMethodMayBeStatic
    def on_stopped(self):
        BdsLogger.put_log('subprocess', 'stopped')
        print('>Server Stopped')
        print('>Manager Stopping...')
        BdsLogger.put_log('manager_core', 'stop')
        print('>Manager Core stopped. Press Ctrl+C to exit.')
        print('Enter \'restart\' to restart Manager.')
        sys.exit()

    def sent_to_all(self, msg_type: str, msg: str):
        clients = self.ws_client.copy()
        for k in clients:
            if not clients[k][0].closed:
                if clients[k][1]:
                    clients[k][0].send(json.dumps({'type': msg_type, 'msg': msg}, ensure_ascii=False))
            else:
                del self.ws_client[k]

    # Save the logs from bds to db
    def save_log(self):
        for line in iter(self.bds.stdout.readline, b''):
            if subprocess.Popen.poll(self.bds) is not None:
                self.on_stopped()
            if line != '':
                line = line.replace('\n', '')
                self.sent_to_all('bds', line)
                BdsLogger.put_log('bds', line)
                print(line)

    # Send commend to bds and get result
    # noinspection PyUnboundLocalVariable
    def cmd_in(self, cmd: str) -> bds_log:
        in_time = datetime.now()
        BdsLogger.put_log('cmd_in', cmd)
        print('>>', cmd)
        self.bds.stdin.write(cmd + '\n')
        self.bds.stdin.flush()
        _log = bds_log(time=in_time, log_type='bds', log='Null')
        for _ in range(5):
            time.sleep(0.1)
            __log = BdsLogger.get_log_all()[-1]
            if __log.time > in_time:
                _log = __log
                break
        return _log
