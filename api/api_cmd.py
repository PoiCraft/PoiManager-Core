import time

from flask import Flask, request
from api.api import BasicApi
from auth.Token import TokenManager
from core.bds import BdsCore
from datetime import datetime

from database import BdsLogger
from database.BdsLogger import write_log


class Api_Cmd(BasicApi):
    def __init__(self, bds: BdsCore, app: Flask, token_manager: TokenManager):
        self.bds = bds
        self.app = app
        self.tokenManager = token_manager
        self.cmd_in()

    def cmd_in(self):
        @self.app.route('/api/cmd/<cmd>/<int:timeout>')
        @self.app.route('/api/cmd/<cmd>')
        @self.tokenManager.require_token
        @write_log(self.bds)
        def api_cmd_in(cmd: str, timeout=None):
            cmd_in_time = datetime.now()
            logs = []

            self.bds.sent_to_all('cmd_in', cmd)
            self.bds.cmd_in(cmd)

            _logs = []

            line = request.args.get('line', None)

            if line is None:
                time.sleep(0.3)
                if timeout:
                    time.sleep(timeout)

                index = -1
                while True:
                    _log = BdsLogger.get_log_all('result')[index]
                    if _log.time >= cmd_in_time:
                        _logs.append(_log)
                        index -= 1
                    else:
                        break
            else:
                line = int(line)
                while True:
                    __logs = []
                    index = -1
                    _n = True
                    while _n:
                        ___logs = BdsLogger.get_log_all('result')
                        if len(___logs) < -index:
                            _n = False
                        _log = ___logs[index]
                        if _log.time >= cmd_in_time:
                            __logs.append(_log)
                            index -= 1
                        else:
                            _n = False
                    if len(__logs) >= line:
                        _logs = __logs
                        break
                    if (datetime.now() - cmd_in_time).seconds >= 3:
                        _logs = __logs
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
