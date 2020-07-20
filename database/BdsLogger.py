from datetime import datetime

from database.database import get_session, bds_log

session = get_session()


def get_log(time: datetime):
    _c = session.query(bds_log).filter_by(key=time)
    return _c.first().value


def get_log_all():
    _c = session.query(bds_log).filter_by(log_type='bds').all()
    return _c


def put_log(log_type: str, value: str) -> None:
    _c = bds_log(time=datetime.now(), log=value, log_type=log_type)
    session.add(_c)
    session.commit()
