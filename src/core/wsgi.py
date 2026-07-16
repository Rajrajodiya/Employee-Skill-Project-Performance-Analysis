"""
WSGI config for ESPPA project.

Exposes the WSGI callable as a module-level variable named ``application``.

Usage:
    gunicorn config.wsgi:application
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')

application = get_wsgi_application()
