from workers import wsgi

from server import app

Default = wsgi.entrypoint(app)
