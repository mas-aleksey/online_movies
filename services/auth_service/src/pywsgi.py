from gevent import monkey
monkey.patch_all()

from gevent.pywsgi import WSGIServer
from app import app, init_app

init_app()
http_server = WSGIServer(('', 5000), app)
http_server.serve_forever()
