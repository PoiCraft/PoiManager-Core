import random
from functools import wraps

from flask import request

from database.ConfigHelper import get_config

token_char = 'abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'


class TokenManager:

    error_msg = {'code': 401, 'type': 'auth', 'msg': 'Unauthorized operation'}
    pass_msg = {'code': 200, 'type': 'auth', 'msg': 'OK'}

    def __init__(self, debug=False):
        self.debug = debug
        self.token = ''.join(random.sample(token_char, int(get_config('token_length'))))
        if self.debug:
            self.token = 'debug'

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
        @wraps(func)
        def wrapper(*args, **kwargs):
            _pass = False
            if request.method == 'GET':
                _pass = self.http_get()
            elif request.method == 'POST':
                _pass = self.json_get()
            if _pass:
                return func(*args, **kwargs)
            else:
                return self.error_msg, 401

        return wrapper
