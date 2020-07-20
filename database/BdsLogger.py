from datetime import datetime

from database.database import get_session, bds_log


def get_log(time: datetime):
    session = get_session()
    _c = session.query(bds_log).filter_by(key=time)
    session.close()
    return _c.first().value


def get_log_all():
    session = get_session()
    _c = session.query(bds_log).filter_by(log_type='bds').all()
    session.close()
    return _c


def put_log(log_type: str, value: str) -> None:
    session = get_session()
    _c = bds_log(time=datetime.now(), log=value, log_type=log_type)
    session.add(_c)
    session.commit()
    session.close()
