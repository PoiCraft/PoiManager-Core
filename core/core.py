import json
import os
import subprocess
import sys
import threading

from flask import Flask, abort
from flask_sockets import Sockets
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.websocket import WebSocket
from werkzeug.exceptions import HTTPException

from auth.Token import TokenManager
from core.bds import BdsCore
from database import BdsLogger
from database.ConfigHelper import get_config
from database.database import get_session, config, bds_log
from loader.PropertiesLoader import PropertiesLoader


class ManagerCore:
    def __init__(self,
                 token_manager: TokenManager,
                 prop_loader: PropertiesLoader,
                 bds: BdsCore,
                 name: str,
                 debug=False):
        self.debug = debug
        self.bds = bds
        self.tokenManager = token_manager
        self.propLoader = prop_loader
        self.t_in = threading.Thread(target=self.terminal_in)
        self.app = Flask(name)
        self.socket = Sockets(self.app)
        self.route_web()
        self.route_ws()
        if self.debug:
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
        @self.app.errorhandler(HTTPException)
        def error(e):
            res = e.get_response()
            res.data = json.dumps({
                'code': e.code,
                'type': 'core',
                'name': e.name,
                'msg': e.description
            })
            res.content_type = 'application/json'
            return res

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
        @self.app.route('/debug/code/<int:code>')
        def debug_err(code: int):
            abort(code)

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

        @self.app.route('/debug/cmd/<cmd_in>')
        def debug_cmd(cmd_in):
            _log = self.bds.cmd_in(cmd_in)
            return {'time': _log.time,
                    'type': _log.log_type,
                    'log': _log.log
                    }

        @self.app.route('/debug/prop')
        def debug_prop():
            return self.propLoader.prop

        @self.app.route('/debug/prop/<key>')
        def debug_prop_value(key):
            value = self.propLoader.get_prop(key)
            body = {
                'code': 200,
                'key': key,
                'value': value
            }
            if value is None:
                body['code'] = 404
                body['msg'] = 'No such key'
            return body, body['code']

        @self.app.route('/debug/prop/<key>/<value>')
        def debug_prop_edit(key, value):
            _e = self.propLoader.edit_prop(key, value)
            return {
                'code': 200,
                'prop': self.propLoader.prop,
                'edited': _e
            }

        @self.app.route('/debug/prop/if_edited')
        def debug_prop_if_edited():
            return {
                'code': 200,
                'msg': self.propLoader.if_edited()
            }

        @self.app.route('/debug/prop/save')
        def debug_prop_save():
            self.propLoader.save()
            return {
                'code': 200,
                'prop': self.propLoader.prop,
                'edited': self.propLoader.if_edited()
            }

    def run(self):
        self.t_in.start()
        if self.debug:
            self.app.debug = True
        # noinspection PyAttributeOutsideInit
        self.http_server = WSGIServer(
            (
                get_config('web_listening_address'),
                int(get_config('web_listening_port'))
            ),
            self.app,
            handler_class=WebSocketHandler)
        self.http_server.serve_forever()
