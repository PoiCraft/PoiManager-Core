import time

from flask import Flask
from api.api import BasicApi
from auth.Token import TokenManager
from core.bds import BdsCore
from datetime import datetime

from database import BdsLogger
from database.database import get_session


class Api_Cmd(BasicApi):
    def __init__(self, bds: BdsCore, app: Flask, token_manager: TokenManager):
        self.bds = bds
        self.app = app
        self.tokenManager = token_manager
        self.cmd_in()

    def cmd_in(self):
        @self.app.route('/api/cmd/<cmd>')
        @self.tokenManager.require_token
        def api_cmd_in(cmd: str):
            cmd_in_time = datetime.now()
            logs = []

            self.bds.cmd_in(cmd)

            if_wait = 0
            while if_wait < 5:
                if_wait += 1
                _log = BdsLogger.get_log_all(log_type='bds')[-1]
                if _log.time < cmd_in_time:
                    if_wait -= 1
                if (datetime.now() - cmd_in_time).seconds > 2.5:
                    break
                time.sleep(0.2)

            _logs = []
            index = -1
            while True:
                _log = BdsLogger.get_log_all('bds')[index]
                if _log.time >= cmd_in_time:
                    _logs.append(_log)
                    index -= 1
                else:
                    break

            for i in range(len(_logs)):
                logs.append(
                    {
                        'time': _logs[-i-1].time,
                        'log': _logs[-i-1].log
                    }
                )

            return self.get_body(
                body_code=200,
                body_type='cmd_log',
                body_content=logs,
                body_msg='OK'
            )
