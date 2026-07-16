"""
Production settings for ESPPA project.

- Disables DEBUG mode
- Configures PostgreSQL via DATABASE_URL (Supabase/Vercel Postgres compatible)
- Enables WhiteNoise for static file serving
- Enforces HTTPS and security headers
"""

import os
from urllib.parse import urlparse, unquote

from .base import *  # noqa: F401, F403

# ── Force Vercel to bundle the self-contained inline template loader ─────────
# Vercel's static analyzer only includes .py files that are DIRECTLY imported
# from the settings entry point. The TEMPLATES config references the loader
# via a string ('apps.esppa.template_loader.InlineTemplateLoader') which
# Django resolves at runtime via import_string(). Vercel's analyzer does NOT
# trace runtime string imports, so the module is excluded from the bundle
# unless we import it explicitly here.
# ── Security overrides ───────────────────────────────────────────────────────
DEBUG = os.environ.get('DJANGO_DEBUG', 'false').lower() in ('true', '1', 'yes')

# ── Database (PostgreSQL via DATABASE_URL or individual env vars) ────────────
# Supabase uses DATABASE_URL format:
#   postgresql://user:password@host:port/dbname?sslmode=require
#
# Set one of:
#   DATABASE_URL — full connection string (Supabase, Vercel Postgres)
#   or individual DB_* vars for traditional PostgreSQL setup

_database_url = os.environ.get('DATABASE_URL')
if _database_url:
    # Parse DATABASE_URL (Supabase / Vercel Postgres / Neon)
    parsed = urlparse(_database_url)
    db_name = parsed.path.lstrip('/')
    if parsed.scheme in ('postgresql', 'postgres'):
        engine = 'django.db.backends.postgresql'
    elif parsed.scheme == 'mysql':
        engine = 'django.db.backends.mysql'
    else:
        engine = 'django.db.backends.postgresql'

    # urllib.parse.urlparse does NOT decode percent-encoded characters
    # (e.g. %40 → @). Decode them manually so psycopg2 gets the real password.
    _user = unquote(parsed.username) if parsed.username else parsed.username
    _password = unquote(parsed.password) if parsed.password else parsed.password

    DATABASES = {  # noqa: F405
        'default': {
            'ENGINE': engine,
            'NAME': db_name,
            'USER': _user,
            'PASSWORD': _password,
            'HOST': parsed.hostname,
            'PORT': parsed.port or '5432',
            'OPTIONS': {
                'sslmode': 'require',
            },
        }
    }
else:
    # Fallback to individual env vars (traditional deployment)
    DATABASES = {  # noqa: F405
        'default': {
            'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
            'NAME': os.environ.get('DB_NAME', 'esppa_db'),
            'USER': os.environ.get('DB_USER', 'esppa_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }

# ── WhiteNoise for static file serving (required on Vercel) ─────────────────
# Vercel triggers collectstatic during build; WhiteNoise serves from STATIC_ROOT
INSTALLED_APPS.insert(0, 'whitenoise.runserver_nostatic')  # noqa: F405
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')  # noqa: F405
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# ── HTTPS & Security ─────────────────────────────────────────────────────────
# Only enforce HTTPS if not on Vercel (Vercel handles SSL at edge)
if not os.environ.get('VERCEL'):
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ── Allowed hosts for Vercel deployment ──────────────────────────────────────
_vercel_url = os.environ.get('VERCEL_URL')
if _vercel_url:
    ALLOWED_HOSTS = [f'.{_vercel_url}', _vercel_url, '.vercel.app']  # noqa: F405
else:
    ALLOWED_HOSTS = os.environ.get(  # noqa: F405
        'ALLOWED_HOSTS', 'localhost,127.0.0.1,.vercel.app',
    ).split(',')

# ── Production logging ───────────────────────────────────────────────────────
LOGGING['root']['level'] = 'WARNING'  # noqa: F405
LOGGING['loggers']['django']['level'] = 'WARNING'  # noqa: F405
LOGGING['loggers']['esppa']['level'] = 'INFO'  # noqa: F405

# Remove file handler on Vercel (ephemeral filesystem)
if os.environ.get('VERCEL'):
    LOGGING['handlers'].pop('file', None)  # noqa: F405
    LOGGING['root']['handlers'] = ['console']  # noqa: F405
    for logger_name in LOGGING['loggers']:  # noqa: F405
        LOGGING['loggers'][logger_name]['handlers'] = ['console']  # noqa: F405
