"""
Development settings for ESPPA project.

- Enables DEBUG mode
- Uses SQLite for local development
- Shows detailed error pages
"""

from .base import *  # noqa: F401, F403

# ── Override for development ─────────────────────────────────────────────────
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# ── Installed apps for development ──────────────────────────────────────────
INSTALLED_APPS += [  # noqa: F405
    'django_extensions',
]

# ── Show debug toolbar only in development ───────────────────────────────────
# INTERNAL_IPS = ['127.0.0.1']

# ── SQLite with faster settings for dev ──────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR.parent / 'db.sqlite3',  # noqa: F405
    }
}

# ── Console email backend for development ────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ── Override logging for detailed dev output ─────────────────────────────────
LOGGING['loggers']['esppa']['level'] = 'DEBUG'  # noqa: F405
