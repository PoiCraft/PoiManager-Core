from database.database import config, get_session, log
from .core import app


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
    _logs = session.query(log).all()
    logs = {}
    for v in _logs:
        logs[str(v.time)] = v.log
    return logs
