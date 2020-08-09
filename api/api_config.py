from flask import Flask

from api.api import BasicApi
from auth.Token import TokenManager
from core.bds import BdsCore
from database.BdsLogger import write_log
from database.ConfigHelper import get_config, put_config
from database.database import get_session, config


class Api_Config(BasicApi):

    """The class of the API for Manager's configs."""

    def __init__(self, app: Flask, token_manager: TokenManager, bds: BdsCore):
        self.app = app
        self.tokenManager = token_manager
        self.bds = bds
        self.get_all_config()
        self.get_one_config()
        self.set_one_config()

    def get_all_config(self):
        @self.app.route('/api/config/all')
        @self.tokenManager.require_token
        @write_log(self.bds)
        def api_get_all_config():
            session = get_session()
            _configs = session.query(config).all()
            session.close()
            configs = {}
            for v in _configs:
                configs[v.key] = v.value
            return self.get_body(
                body_code=200,
                body_type='config_all',
                body_content=configs,
                body_msg='OK'
            )

    def get_one_config(self):
        @self.app.route('/api/config/one/<key>')
        @self.tokenManager.require_token
        @write_log(self.bds)
        def api_get_one_config(key: str):
            _c = get_config(key)
            if _c is None:
                return self.get_body(
                    body_code=404,
                    body_type=f'config_get_{key}',
                    body_content=None,
                    body_msg='No such key'
                )
            else:
                return self.get_body(
                    body_code=200,
                    body_type=f'config_{key}',
                    body_content=_c,
                    body_msg='OK'
                )

    def set_one_config(self):
        @self.app.route('/api/config/set/<key>/<value>')
        @self.tokenManager.require_token
        @write_log(self.bds)
        def api_set_one_config(key: str, value: str):
            _c = put_config(key, value)
            return self.get_body(
                body_code=200,
                body_type=f'config_set_{key}',
                body_content=_c,
                body_msg='OK'
            )
