import json

from geventwebsocket.websocket import WebSocket


class WebSocketCollector:
    ws_client = {}
    ws_client_len = 0

    def add(self, ws: WebSocket):
        self.ws_client[self.ws_client_len] = [ws, False]
        self.ws_client_len += 1
        return self.ws_client_len - 1

    def update(self, ws_id: int):
        client = self.ws_client[ws_id]
        if client[1] is False:
            to_return = 1
        else:
            to_return = 0
        client[1] = True
        self.ws_client[ws_id] = client
        return to_return

    def check(self, ws_id: int):
        return self.ws_client[ws_id][1]

    def sent_to_all(self, msg_type: str, msg: str, status=True, ignore=False):
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
                            'status': status
                        },
                        ensure_ascii=False))
            else:
                del self.ws_client[k]