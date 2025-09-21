"""
ASGI config for packet_analyzer project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# packet_analyzer/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import capture.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packet_analyzer.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            capture.routing.websocket_urlpatterns
        )
    ),
})