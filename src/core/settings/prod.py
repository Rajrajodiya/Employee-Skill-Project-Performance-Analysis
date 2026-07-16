"""
Production settings for ESPPA project.

- Disables DEBUG mode
- Configures PostgreSQL (default) / MySQL
- Enforces HTTPS and security headers
"""

from .base import *  # noqa: F401, F403

# ── Security overrides ───────────────────────────────────────────────────────
DEBUG = False

# ── Database (PostgreSQL recommended for production) ─────────────────────────
# To use PostgreSQL, install: pip install psycopg2-binary
# Then set these environment variables:
#   DB_NAME=esppa_db, DB_USER=esppa_user, DB_PASSWORD=..., DB_HOST=localhost, DB_PORT=5432
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),  # noqa: F405
        'NAME': config('DB_NAME', default='esppa_db'),  # noqa: F405
        'USER': config('DB_USER', default='esppa_user'),  # noqa: F405
        'PASSWORD': config('DB_PASSWORD', default=''),  # noqa: F405
        'HOST': config('DB_HOST', default='localhost'),  # noqa: F405
        'PORT': config('DB_PORT', default='5432'),  # noqa: F405
    }
}

# ── HTTPS & Security ─────────────────────────────────────────────────────────
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ── Production logging ───────────────────────────────────────────────────────
LOGGING['root']['level'] = 'WARNING'  # noqa: F405
LOGGING['loggers']['django']['level'] = 'WARNING'  # noqa: F405
LOGGING['loggers']['esppa']['level'] = 'INFO'  # noqa: F405

# ── Static files serving (for production, use WhiteNoise or CDN) ────────────
# INSTALLED_APPS.insert(0, 'whitenoise.runserver_nostatic')  # noqa: F405
# MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')  # noqa: F405
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
