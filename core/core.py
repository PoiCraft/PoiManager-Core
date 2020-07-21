import os
import subprocess
import sys
import threading

from flask import Flask
from flask_sockets import Sockets
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.websocket import WebSocket

from database import BdsLogger
from database.ConfigHelper import get_config
from database.database import get_session, config, bds_log
from core.bds import BdsCore


class ManagerCore:
    def __init__(self, manager_root: str, debug=False):
        self.manager_root = manager_root
        self.app = Flask(__name__)
        self.socket = Sockets(self.app)
        self.route_web()
        self.route_debug()
        self.debug = debug
        if not debug:
            self.http_server = WSGIServer(
                (
                    get_config('web_listening_address'),
                    int(get_config('web_listening_port'))
                ),
                self.app,
                handler_class=WebSocketHandler)
        self.bds = BdsCore()

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
        @self.app.route('/')
        def index():
            return 'Hello World'

    def route_debug(self):
        # For debug
        @self.app.route('/debug/config')
        def debug_config():
            session = get_session()
            _configs = session.query(config).all()
            session.close()
            configs = {}
            for v in _configs:
                configs[v.key] = v.value
            return configs

        @self.app.route('/debug/log')
        def debug_log():
            session = get_session()
            _logs = session.query(bds_log).all()
            session.close()
            logs = {}
            for v in _logs:
                logs[str(v.time)] = [v.log_type, v.log]
            return logs

        @self.socket.route('/debug/cmd')
        def cmd(ws: WebSocket):
            self.bds.add_ws(ws)
            while not ws.closed:
                message = ws.receive()
                if message is not None:
                    self.bds.sent_to_all('cmd_in', message)
                    if message.split(' ')[0] in self.bds.danger_cmd:
                        self.bds.sent_to_all('bds', 'Not supported via WebSocket')
                    else:
                        result = self.bds.cmd_in(message)
                        if result.log == 'Null':
                            self.bds.sent_to_all('bds', 'done')

        @self.app.route('/debug/cmd/<cmd_in>')
        def debug_cmd(cmd_in):
            _log = self.bds.cmd_in(cmd_in)
            return {'time': _log.time,
                    'type': _log.log_type,
                    'log': _log.log
                    }

    def run(self):
        t_in = threading.Thread(target=self.terminal_in)
        t_in.start()
        if self.debug:
            self.app.run(get_config('web_listening_address'), int(get_config('web_listening_port')), debug=True)
        else:
            self.http_server.serve_forever()
