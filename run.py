import sys
from gevent.pywsgi import WSGIServer

from config.config import get_config

from bds.control import bds

if sys.argv[1] == 'debug':
    from web.debug import app
    app.run(debug=True,
            host=get_config('web_listening_address'),
            port=int(get_config('web_listening_port'))
            )
else:
    from web.core import app
    http_server = WSGIServer(
        (
            get_config('web_listening_address'),
            int(get_config('web_listening_port'))
        ),
        app)
    http_server.serve_forever()
