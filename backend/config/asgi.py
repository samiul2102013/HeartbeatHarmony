import os
import django
import socketio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.asgi import get_asgi_application
from apps.community.socketio_server import sio

django_asgi_app = get_asgi_application()

application = socketio.ASGIApp(sio, django_asgi_app)