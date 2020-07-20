import sys
from gevent.pywsgi import WSGIServer
from database.ConfigHelper import get_config
from core.core import app

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
