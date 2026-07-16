"""
WSGI config for ESPPA project.

Exposes the WSGI callable as a module-level variable named ``application``.
Works with both traditional gunicorn and Vercel serverless.

Usage:
    gunicorn core.wsgi:application       # Traditional
    vercel dev                            # Vercel local
"""

import os

from django.core.wsgi import get_wsgi_application

# Vercel sets this via vercel.json env section
# Falls back to dev for local development
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')

application = get_wsgi_application()
