import random
from database.ConfigHelper import get_config

from flask import request

token_char = 'abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'


class TokenManager:

    def __init__(self):
        self.token = ''.join(random.sample(token_char, int(get_config('token_length'))))

    def getToken(self):
        return self.token

    def checkToken(self, token: str):
        return token == self.token

    def http_get(self):
        _token = request.args.get('token', '')
        return self.checkToken(_token)

    def json_get(self):
        _token = ''
        __json = request.get_json()
        if __json:
            _token = __json.get('token', '')
        else:
            _token = request.form.get('token', '')
        return self.checkToken(_token)

    def require_token(self, func):
        def wrapper(*args, **kwargs):
            _pass = False
            if request.method == 'GET':
                _pass = self.http_get()
            elif request.method == 'POST':
                _pass = self.json_get()
            if _pass:
                return func(*args, **kwargs)
            else:
                return {'code': '401', 'type': 'auth', 'msg': 'Unauthorized operation'}, 401
        return wrapper
