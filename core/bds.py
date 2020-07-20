import time
import subprocess
from datetime import datetime
import threading
from database import BdsLogger
from database.ConfigHelper import get_config
from database.database import bds_log

# Run bds
bds = subprocess.Popen(
    'cd %s \n %s' % (
        get_config('bedrock_server_root'),
        get_config('bedrock_server_script')
    ),
    shell=True,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    universal_newlines=True
)


# Save the logs from bds to db
def save_log():
    for line in iter(bds.stdout.readline, b''):
        if line != '':
            line = line.replace('\n', '')
            BdsLogger.put_log('bds', line)
            print(line)


# Keep the `save_log` running
logger = threading.Thread(target=save_log)
logger.start()


# Send commend to bds and get result
# noinspection PyUnboundLocalVariable
def cmd_in(cmd: str) -> bds_log:
    in_time = datetime.now()
    BdsLogger.put_log('web_cmd_in', cmd)
    bds.stdin.write(cmd + '\n')
    bds.stdin.flush()
    _log = bds_log(time=in_time, log_type='bds', log='Null')
    for _ in range(5):
        time.sleep(0.1)
        __log = BdsLogger.get_log_all()[-1]
        print(_log.time, in_time)
        if _log.time > in_time:
            _log = __log
            break
    return _log
