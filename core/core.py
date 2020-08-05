import json
import threading

from flask import Flask, abort, render_template
from flask_sockets import Sockets
from gevent.pywsgi import WSGIServer
# noinspection PyPackageRequirements
from geventwebsocket.handler import WebSocketHandler
from werkzeug.exceptions import HTTPException

from api.api_cmd import Api_Cmd
from auth.Token import TokenManager
from core.bds import BdsCore
from database.ConfigHelper import get_config
from loader.PropertiesLoader import PropertiesLoader
from api.api_log import Api_Log
from api.api_config import Api_Config
from api.api_prop import Api_Prop
from api.ws_cmd import Ws_Cmd


class ManagerCore:
    # noinspection PyUnusedLocal
    def __init__(self,
                 app: Flask,
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
        self.app = app
        self.socket = Sockets(self.app)
        self.api_log = Api_Log(
            app=self.app,
            token_manager=self.tokenManager,
            bds=self.bds
        )
        self.api_config = Api_Config(
            app=self.app,
            token_manager=self.tokenManager
        )
        self.api_ws_cmd = Ws_Cmd(
            bds=self.bds,
            socket=self.socket,
            token_manager=self.tokenManager
        )
        self.api_prop = Api_Prop(
            app=self.app,
            token_manager=self.tokenManager,
            prop_loader=self.propLoader
        )
        self.api_cmd = Api_Cmd(
            app=self.app,
            bds=self.bds,
            token_manager=self.tokenManager
        )

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

        @self.app.route('/')
        def index():
            return render_template('index.html')

        if self.debug:
            self.route_debug()

    def restart_bds(self):
        self.bds.bds_restart()

    def terminal_in(self):
        while True:
            in_cmd = input()
            if in_cmd == "manager_token":
                print(self.tokenManager.token)
                continue
            self.bds.sent_to_all('cmd_in', in_cmd)
            if in_cmd == 'restart':
                self.restart_bds()
            else:
                self.bds.cmd_in(in_cmd)

    def route_debug(self):
        # For debug
        @self.app.route('/debug/code/<int:code>')
        def debug_err(code: int):
            abort(code)

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
