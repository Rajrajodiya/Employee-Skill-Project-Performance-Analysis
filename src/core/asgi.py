"""
ASGI config for ESPPA project.

Exposes the ASGI callable as a module-level variable named ``application``.

Usage:
    uvicorn config.asgi:application
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')

application = get_asgi_application()
