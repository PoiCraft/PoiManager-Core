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
    # Init flask
    app = Flask(__name__)
    socket = Sockets(app)

    def __init__(self, debug=False):
        self.web()
        if debug:
            self.debug()
        self.http_server = WSGIServer(
            (
                get_config('web_listening_address'),
                int(get_config('web_listening_port'))
            ),
            self.app,
            handler_class=WebSocketHandler)
        self.bds = BdsCore(self.http_server, self.app, self.socket)

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

    def web(self):
        # Home
        @self.app.route('/')
        def index():
            return 'Hello World'

    def debug(self):
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
                    if message == 'restart':
                        ws.close('200', b'restarting...')
                        self.restart_bds()
                    else:
                        result = self.bds.cmd_in(message)
                        if result.log == 'Null':
                            self.bds.sent_to_all('bds', 'done')

        @self.app.route('/debug/cmd/<cmd>')
        def debug_cmd(cmd_in):
            _log = self.bds.cmd_in(cmd_in)
            return {'time': _log.time,
                    'type': _log.log_type,
                    'log': _log.log
                    }

    def run(self):
        t_in = threading.Thread(target=self.terminal_in)
        t_in.start()
        self.http_server.serve_forever()
