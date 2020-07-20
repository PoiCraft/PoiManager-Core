from database.database import get_session, config

default = dict(
    bedrock_server='cd bedrock_server && LD_LIBRARY_PATH=. ./bedrock_server ',
    web_listening_address='127.0.0.1',
    web_listening_port='5500'
)

session = get_session()


def get_config(key: str):
    _c = session.query(config).filter_by(key=key)
    return _c.first().value


def put_config(key: str, value: str):
    _c = session.query(config).filter_by(key=key)
    _c.value = value
    session.commit()


def init():
    for key in default:
        try:
            _config = config(key=key, value=default[key])
            session.add(_config)
            session.commit()
        finally:
            pass
    session.close()
