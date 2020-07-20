from flask import Flask
from database import database

# Init flask
app = Flask(__name__)


# Home
@app.route('/')
def index():
    return 'Hello World'


# For debug
@app.route('/debug/config')
def debug_config():
    session = database.get_session()
    _configs = session.query(database.config).all()
    configs = {}
    for v in _configs:
        configs[v.key] = v.value
    return configs


@app.route('/debug/log')
def debug_log():
    session = database.get_session()
    _logs = session.query(database.bds_log).all()
    logs = {}
    for v in _logs:
        logs[str(v.time)] = [v.log_type, v.log]
    return logs
