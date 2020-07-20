import sys
from database.database import get_session, config


def get_script():
    if 'linux' in sys.platform:
        return 'LD_LIBRARY_PATH=. ./bedrock_server'
    elif 'win' in sys.platform:
        return './bedrock_server.exe'


default = dict(
    bedrock_server_root='bedrock_server',
    bedrock_server_script=get_script(),
    web_listening_address='127.0.0.1',
    web_listening_port='5500'
)


def get_config(key: str):
    session = get_session()
    _c = session.query(config).filter_by(key=key)
    session.close()
    return _c.first().value


def put_config(key: str, value: str):
    session = get_session()
    _c = session.query(config).filter_by(key=key).first()
    session.close()
    _c.value = value
    session.commit()
    session.close()


def init():
    session = get_session()
    for key in default:
        try:
            _config = config(key=key, value=default[key])
            session.add(_config)
            session.commit()
        finally:
            pass
    session.close()


# noinspection PyBroadException
def print_and_edit():
    session = get_session()
    _configs = session.query(config).all()
    session.close()
    configs_keys = []
    for v in _configs:
        configs_keys.append(v.key)
        print('%s %s=%s' % (
            len(configs_keys),
            v.key,
            v.value
        ))
    print('Enter 0 to Exit')
    key_index = input('Enter the number before the config you want to edit: ')
    if key_index == '0':
        return
    try:
        _key = configs_keys[int(key_index) - 1]
        _value = input('Then enter the value: ')
        put_config(_key, _value)
    except:
        print('Failed!')
    print_and_edit()
