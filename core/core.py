from flask import Flask
from database.database import get_session, config, bds_log
from core.bds import cmd_in

# Init flask
app = Flask(__name__)


# Home
@app.route('/')
def index():
    return 'Hello World'


# For debug
@app.route('/debug/config')
def debug_config():
    session = get_session()
    _configs = session.query(config).all()
    configs = {}
    for v in _configs:
        configs[v.key] = v.value
    return configs


@app.route('/debug/log')
def debug_log():
    session = get_session()
    _logs = session.query(bds_log).all()
    logs = {}
    for v in _logs:
        logs[str(v.time)] = [v.log_type, v.log]
    return logs


@app.route('/debug/cmd/<cmd>')
def debug_cmd(cmd):
    _log = cmd_in(cmd)
    return {'time': _log.time,
            'type': _log.log_type,
            'log': _log.log
            }