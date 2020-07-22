import json
import os
import subprocess
import sys
import threading

from flask import Flask
from flask_sockets import Sockets
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.websocket import WebSocket

from auth.Token import TokenManager
from database import BdsLogger
from database.ConfigHelper import get_config
from database.database import get_session, config, bds_log
from core.bds import BdsCore


class ManagerCore:
    def __init__(self, token_manager: TokenManager, bds: BdsCore, name: str):
        self.bds = bds
        self.tokenManager = token_manager
        self.t_in = threading.Thread(target=self.terminal_in)
        self.app = Flask(name)
        self.socket = Sockets(self.app)
        self.route_web()
        self.route_ws()
        self.route_debug()

    def restart_bds(self):
        self.bds.sent_to_all('manager', 'restart')
        BdsLogger.put_log('manager', 'restart')
        if subprocess.Popen.poll(self.bds.bds) is None:
            self.bds.bds.stdin.write('stop')
            self.bds.bds.stdin.flush()
        print('>restarting...')
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def terminal_in(self):
        while True:
            in_cmd = input()
            BdsLogger.put_log('cmd_in', in_cmd)
            self.bds.sent_to_all('cmd_in', in_cmd)
            if in_cmd == 'restart':
                self.restart_bds()
            else:
                self.bds.cmd_in(in_cmd)

    def route_web(self):
        # Home
        @self.app.route('/', methods=['GET', 'POST'])
        def index():
            return 'Hello World'

    def route_ws(self):
        # noinspection PyUnusedLocal
        def cmd_in_via_ws(cmd_in):
            if cmd_in is None:
                return
            self.bds.sent_to_all('cmd_in', cmd_in)
            if cmd_in.split(' ')[0] in self.bds.danger_cmd:
                self.bds.sent_to_all('bds', 'Not supported via WebSocket')
            else:
                result = self.bds.cmd_in(cmd_in)
                if result.log == 'Null':
                    self.bds.sent_to_all('bds', 'done')

        @self.socket.route('/ws/cmd')
        def cmd(ws: WebSocket):
            ws_id = self.bds.add_ws(ws)
            while not ws.closed:
                message = ws.receive()
                if message is not None:
                    # noinspection PyBroadException
                    msg = {'token': '', 'cmd': None}
                    # noinspection PyBroadException
                    try:
                        msg = json.loads(message)
                    except:
                        msg['cmd'] = message
                    if self.tokenManager.checkToken(msg.get('token', '')) or self.bds.check_ws(ws_id):
                        result = self.bds.update_ws(ws_id)
                        if result == 1:
                            ws.send(json.dumps(self.tokenManager.pass_msg, ensure_ascii=False))
                        cmd_in_via_ws(msg.get('cmd', None))
                    else:
                        ws.send(json.dumps(self.tokenManager.error_msg, ensure_ascii=False))

    def route_debug(self):
        # For debug
        @self.app.route('/debug/config')
        @self.tokenManager.require_token
        def debug_config():
            session = get_session()
            _configs = session.query(config).all()
            session.close()
            configs = {}
            for v in _configs:
                configs[v.key] = v.value
            return configs

        @self.app.route('/debug/log')
        @self.tokenManager.require_token
        def debug_log():
            session = get_session()
            _logs = session.query(bds_log).all()
            session.close()
            logs = {}
            for v in _logs:
                logs[str(v.time)] = [v.log_type, v.log]
            return logs

        @self.app.route('/debug/cmd/<cmd_in>')
        @self.tokenManager.require_token
        def debug_cmd(cmd_in):
            _log = self.bds.cmd_in(cmd_in)
            return {'time': _log.time,
                    'type': _log.log_type,
                    'log': _log.log
                    }

    def run(self):
        self.t_in.start()
        # noinspection PyAttributeOutsideInit
        self.http_server = WSGIServer(
            (
                get_config('web_listening_address'),
                int(get_config('web_listening_port'))
            ),
            self.app,
            handler_class=WebSocketHandler)
        self.http_server.serve_forever()
