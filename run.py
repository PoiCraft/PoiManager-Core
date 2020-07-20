import sys
from gevent.pywsgi import WSGIServer
from database.config import get_config
from web.core import app
from core.bds import cmd_in


@app.route('/debug/cmd/<cmd>')
def debug_cmd(cmd):
    _log = cmd_in(cmd)
    return {'time': _log.time,
            'type': _log.log_type,
            'log': _log.log
            }


# Run web server
if sys.argv[1] == 'debug':
    app.debug = True
http_server = WSGIServer(
    (
        get_config('web_listening_address'),
        int(get_config('web_listening_port'))
    ),
    app)
http_server.serve_forever()
