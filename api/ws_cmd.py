import json

from flask_sockets import Sockets
from geventwebsocket.websocket import WebSocket

from auth.Token import TokenManager
from core.bds import BdsCore


class Ws_Cmd:

    def __init__(self, bds: BdsCore, socket: Sockets, token_manager: TokenManager):
        self.socket = socket
        self.bds = bds
        self.tokenManager = token_manager
        self.ws_cmd_in()

    # noinspection PyUnusedLocal
    def cmd_in_via_ws(self, cmd_in):
        if cmd_in is None:
            return
        self.bds.sent_to_all('cmd_in', cmd_in)
        if cmd_in.split(' ')[0] in self.bds.danger_cmd:
            self.bds.sent_to_all('bds', 'Not supported via WebSocket')
        else:
            result = self.bds.cmd_in(cmd_in)
            if result.log == 'Null':
                self.bds.sent_to_all('bds', 'done')

    def ws_cmd_in(self):
        @self.socket.route('/api/ws/cmd')
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
                        self.cmd_in_via_ws(msg.get('cmd', None))
                    else:
                        ws.send(json.dumps(self.tokenManager.error_msg, ensure_ascii=False))
