"""
Django settings for ESPPA project.

All configuration in one file. Use environment variables to switch
between development and production modes.

Environment variables:
  DJANGO_DEBUG        Set to 'true' or '1' to enable debug mode (default: false)
  DJANGO_SECRET_KEY   Django secret key (default: development-only fallback)
  ALLOWED_HOSTS       Comma-separated list of allowed hosts
  DATABASE_URL        Full PostgreSQL connection string (optional, uses SQLite otherwise)
  DB_*                Individual database env vars (DB_ENGINE, DB_NAME, etc.)
"""

import os
import sys
import importlib.util
from pathlib import Path
from urllib.parse import urlparse, unquote
from decouple import config, Csv

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BASE_DIR.parent
APPS_DIR = BASE_DIR / 'apps'
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

# ═════════════════════════════════════════════════════════════════════════════
#  Security
# ═════════════════════════════════════════════════════════════════════════════

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = config('DJANGO_DEBUG', default='false', cast=bool) or config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# ═════════════════════════════════════════════════════════════════════════════
#  Application Definition
# ═════════════════════════════════════════════════════════════════════════════

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
    'widget_tweaks',
    'rest_framework',
    'drf_spectacular',
    'django_cotton',
]

LOCAL_APPS = [
    'apps.esppa',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Add django-extensions when available (dev convenience)
if importlib.util.find_spec('django_extensions'):
    INSTALLED_APPS += ['django_extensions']

# Whitenoise for static file serving
INSTALLED_APPS.insert(0, 'whitenoise.runserver_nostatic')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(APPS_DIR, 'esppa', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ═════════════════════════════════════════════════════════════════════════════
#  Database
# ═════════════════════════════════════════════════════════════════════════════

_database_url = os.environ.get('DATABASE_URL')
if _database_url:
    parsed = urlparse(_database_url)
    db_name = parsed.path.lstrip('/')
    engine = 'django.db.backends.postgresql'
    _user = unquote(parsed.username) if parsed.username else parsed.username
    _password = unquote(parsed.password) if parsed.password else parsed.password
    DATABASES = {
        'default': {
            'ENGINE': engine,
            'NAME': db_name,
            'USER': _user,
            'PASSWORD': _password,
            'HOST': parsed.hostname,
            'PORT': parsed.port or '5432',
            'OPTIONS': {'sslmode': 'require'},
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': PROJECT_ROOT / 'db.sqlite3',
        }
    }

# ═════════════════════════════════════════════════════════════════════════════
#  Password Validation
# ═════════════════════════════════════════════════════════════════════════════

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ═════════════════════════════════════════════════════════════════════════════
#  Internationalization
# ═════════════════════════════════════════════════════════════════════════════

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ═════════════════════════════════════════════════════════════════════════════
#  Static & Media Files
# ═════════════════════════════════════════════════════════════════════════════

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'static'),
]
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')

STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ═════════════════════════════════════════════════════════════════════════════
#  HTTPS & Security (only when DEBUG is False)
# ═════════════════════════════════════════════════════════════════════════════

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Console email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ═════════════════════════════════════════════════════════════════════════════
#  Logging
# ═════════════════════════════════════════════════════════════════════════════

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(PROJECT_ROOT, 'server.log'),
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'WARNING' if not DEBUG else 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING' if not DEBUG else 'INFO',
            'propagate': False,
        },
        'esppa': {
            'handlers': ['console', 'file'],
            'level': 'INFO' if not DEBUG else 'DEBUG',
            'propagate': False,
        },
    },
}

# ═════════════════════════════════════════════════════════════════════════════
#  Crispy Forms
# ═════════════════════════════════════════════════════════════════════════════

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ═════════════════════════════════════════════════════════════════════════════
#  Authentication
# ═════════════════════════════════════════════════════════════════════════════

LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'
SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# ═════════════════════════════════════════════════════════════════════════════
#  Django REST Framework
# ═════════════════════════════════════════════════════════════════════════════

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/minute',
        'user': '100/minute',
    },
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
}

# ═════════════════════════════════════════════════════════════════════════════
#  drf-spectacular (Swagger/OpenAPI)
# ═════════════════════════════════════════════════════════════════════════════

SPECTACULAR_SETTINGS = {
    'TITLE': 'ESPPA API',
    'DESCRIPTION': 'Employee Skill & Project Performance Analyzer - REST API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
