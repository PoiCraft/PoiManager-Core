from datetime import datetime
from functools import wraps

from flask import request

from database.database import get_session, bds_log


def get_log(time: datetime):
    session = get_session()
    _c = session.query(bds_log).filter_by(key=time)
    session.close()
    return _c.first().value


def get_log_all(log_type='bds'):
    session = get_session()
    if log_type is None:
        _c = session.query(bds_log).all()
    else:
        _c = session.query(bds_log).filter_by(log_type=log_type).all()
    session.close()
    return _c


def put_log(log_type: str, value: str) -> None:
    session = get_session()
    _c = bds_log(time=datetime.now(), log=value, log_type=log_type)
    print(f'{log_type} > {value}')
    session.add(_c)
    session.commit()
    session.close()


def clear_log():
    session = get_session()
    _c = session.query(bds_log).delete()
    session.commit()
    session.close()


def write_log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        log_type = request.args.get('type', None)
        log = request.args.get('msg', None)
        if (log_type is not None) and (log is not None):
            put_log(log_type, log)
        return func(*args, **kwargs)

    return wrapper
