import sys
from datetime import datetime

from database.database import get_session, log

session = get_session()


def get_log(time: datetime):
    _c = session.query(log).filter_by(key=time)
    return _c.first().value


def put_log(value: str) -> None:
    _c = log(time=datetime.now(), log=value)
    session.add(_c)
    session.commit()