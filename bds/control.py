import subprocess
import threading

from config.config import get_config
from .log import put_log

bds = subprocess.Popen(
    get_config('bedrock_server'),
    shell=True,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    universal_newlines=True
)


def save_log():
    for line in iter(bds.stdout.readline, b''):
        if line != '':
            line = line.replace('\n', '')
            put_log(line)
            print(line)


logger = threading.Thread(target=save_log)
logger.start()
