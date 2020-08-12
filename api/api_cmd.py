import time

from flask import Flask, request
from api.api import BasicApi
from auth.Token import TokenManager
from core.bds import BdsCore
from datetime import datetime

from database import BdsLogger
from database.BdsLogger import write_log
from database.database import get_session, bds_log


class Api_Cmd(BasicApi):
    def __init__(self, bds: BdsCore, app: Flask, token_manager: TokenManager):
        self.bds = bds
        self.app = app
        self.tokenManager = token_manager
        self.cmd_in()

    def cmd_in(self):
        @self.app.route('/api/cmd/<cmd>')
        @self.tokenManager.require_token
        @write_log(self.bds)
        def api_cmd_in(cmd: str):
            cmd_in_time = datetime.now()
            logs = []

            ignore = request.args.get('ignore', None) == 'true'

            self.bds.cmd_in(cmd, ignore=ignore)

            _logs = []

            line = request.args.get('line', None)
            wait_sec = int(request.args.get('timeout', 3))

            if line is None:

                return self.get_body(
                    body_code=400,
                    body_type='cmd_log',
                    body_msg='Error, missing "line"',
                    body_content=None
                )

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
                            continue
                        _log = ___logs[index]
                        if _log.time >= cmd_in_time:
                            __logs.append(_log)
                            index -= 1
                        else:
                            _n = False
                    if len(__logs) >= line:
                        _logs = __logs
                        break
                    if wait_sec == 0:
                        continue
                    if (datetime.now() - cmd_in_time).seconds >= wait_sec:
                        _logs = __logs
                        break

            if ignore:
                session = get_session()
                for v in _logs:
                    session.delete(session.query(bds_log).get(v.time))
                _l = f'The {len(_logs)} lines of log above has been removed from db.'
                BdsLogger.put_log('cmd_log', _l, ignore=True)

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
