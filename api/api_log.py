from flask import Flask

from api.api import BasicApi
from auth.Token import TokenManager
from database import BdsLogger


class Api_Log(BasicApi):
    def __init__(self, app: Flask, token_manager: TokenManager):
        self.app = app
        self.tokenManager = token_manager
        self.log_all()
        self.log_type()
        self.log_type_or_length()

    # noinspection PyMethodMayBeStatic
    def log2dict(self, log_list):
        _log_list = []
        for _log in log_list:
            _log_list.append({'time': _log.time,
                              'type': _log.log_type,
                              'log': _log.log
                              })
        return _log_list

    def log_all(self):
        @self.app.route('/api/log/all')
        @self.tokenManager.require_token
        def api_log_all():
            _log = BdsLogger.get_log_all(log_type=None)
            return self.get_body(body_code=200,
                                 body_type='log_all',
                                 body_content=self.log2dict(_log),
                                 body_msg='OK'
                                 )

    def log_type(self):
        @self.app.route('/api/log/type/<log_type>')
        @self.tokenManager.require_token
        def api_log_type(log_type: str):
            _log = BdsLogger.get_log_all(log_type=log_type)
            if _log is None:
                return self.get_body(
                    body_code=404,
                    body_type=f'log_{log_type}',
                    body_content=None,
                    body_msg='No such type'
                )
            else:
                return self.get_body(
                    body_code=200,
                    body_type=f'log_{log_type}',
                    body_content=self.log2dict(_log),
                    body_msg='OK'
                )

    def log_type_or_length(self):
        @self.app.route('/api/log/all/<int:length>')
        @self.app.route('/api/log/type/<log_type>/<int:length>')
        @self.tokenManager.require_token
        def api_log_type_or_length(length, log_type=None):
            _log = BdsLogger.get_log_all(log_type=log_type)
            if log_type is None:
                log_type = 'all'
            if _log is None:
                return self.get_body(
                    body_code=404,
                    body_type=f'log_{log_type}',
                    body_content=_log,
                    body_msg='No such type'
                )
            else:
                if len(_log) < length:
                    return self.get_body(
                        body_code=200,
                        body_type=f'log_{log_type}',
                        body_content=self.log2dict(_log),
                        body_msg='OK'
                    )
                else:
                    start = len(_log) - length
                    stop = len(_log)
                    print(start, stop)
                    return self.get_body(
                        body_code=200,
                        body_type=f'log_{log_type}',
                        body_content=self.log2dict(_log)[start:stop],
                        body_msg='OK'
                    )
