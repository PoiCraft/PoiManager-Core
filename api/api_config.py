from flask import Flask

from api.api import BasicApi
from auth.Token import TokenManager
from database.ConfigHelper import get_config, put_config
from database.database import get_session, config


class Api_Config(BasicApi):

    def __init__(self, app: Flask, token_manager: TokenManager):
        self.app = app
        self.tokenManager = token_manager
        self.get_all_config()
        self.get_one_config()
        self.set_one_config()

    def get_all_config(self):
        @self.app.route('/api/config/all')
        def api_get_all_config():
            session = get_session()
            _configs = session.query(config).all()
            session.close()
            configs = {}
            for v in _configs:
                configs[v.key] = v.value
            return self.get_body(
                200,
                'config_all',
                configs
            )

    def get_one_config(self):
        @self.app.route('/api/config/one/<key>')
        def api_get_one_config(key: str):
            _c = get_config(key)
            if _c is None:
                return self.get_body(
                    404,
                    f'config_get_{key}',
                    None
                )
            else:
                return self.get_body(
                    200,
                    f'config_{key}',
                    _c
                )

    def set_one_config(self):
        @self.app.route('/api/config/set/<key>/<value>')
        def api_set_one_config(key: str, value: str):
            _c = put_config(key, value)
            return self.get_body(
                200,
                f'config_set_{key}',
                _c
            )
