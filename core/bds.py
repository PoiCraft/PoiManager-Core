import os
import time
import subprocess
from datetime import datetime
import threading

from geventwebsocket.websocket import WebSocket

from database import BdsLogger
from database.ConfigHelper import get_config, get_session
from database.database import bds_log
import sys
import json


class BdsCore:

    danger_cmd = [
        'restart',
        'stop'
    ]
    ws_client = {}

    def add_ws(self, ws: WebSocket):
        self.ws_client[len(self.ws_client)] = ws

    def __init__(self):
        if 'linux' in sys.platform:
            self.script = 'cd %s \n %s' % (
                get_config('bedrock_server_root'),
                get_config('bedrock_server_script')
            )
            self.shell = True
        elif 'win' in sys.platform:
            self.script = os.path.join(
                get_config('bedrock_server_root'),
                get_config('bedrock_server_script')
            )
            self.shell = False
        self.bds = subprocess.Popen(
            self.script,
            shell=self.shell,
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
        print('>Manager Stopping...')
        BdsLogger.put_log('manager_core', 'stop')
        print('>Manager Core stopped. Press Ctrl+C to exit.')
        print('Enter \'restart\' to restart Manager.')
        sys.exit()

    def sent_to_all(self, msg_type: str, msg: str):
        clients = self.ws_client.copy()
        for k in clients:
            if not clients[k].closed:
                clients[k].send(json.dumps({'type': msg_type, 'msg': msg}, ensure_ascii=False))
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
