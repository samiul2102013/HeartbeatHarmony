from pathlib import Path
from datetime import timedelta
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '*').split(',') if host.strip()]
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv('CSRF_TRUSTED_ORIGINS', 'https://*.railway.app,https://*.vercel.app').split(',') if origin.strip()]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'channels',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.checkins',
    'apps.habits',
    'apps.study',
    'apps.community',
    'apps.pricing',
    'apps.core',
    'apps.notifications',
    'apps.iap',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
AUTH_USER_MODEL = 'accounts.User'

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/minute',
    },
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Disable APPEND_SLASH for REST API — allows requests without trailing slashes
APPEND_SLASH = False

# Apple App Store In-App Purchase
APPLE_SHARED_SECRET = os.getenv('APPLE_SHARED_SECRET', '')
APPLE_CLIENT_ID = os.getenv('APPLE_CLIENT_ID', 'com.icsncardiology.heartbeatharmony')

# Google Play In-App Purchase — service account JSON (inline or file path)
GOOGLE_SERVICE_ACCOUNT_KEY_JSON = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY_JSON', '')
GOOGLE_SERVICE_ACCOUNT_KEY_PATH = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY_PATH', '')

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
}

cors_origins_env = os.getenv('CORS_ORIGINS', '')
CORS_ALLOW_ALL_ORIGINS = DEBUG or '*' in [o.strip() for o in cors_origins_env.split(',') if o.strip()]
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins_env.split(',') if origin.strip() and origin.strip() != '*']

# Development / testing bypass for email verification (use only in dev/staging)
ALLOW_DEV_BYPASS = os.getenv('ALLOW_DEV_BYPASS', 'False') == 'True'
DEV_BYPASS_VALUE = os.getenv('DEV_BYPASS_VALUE', '123456')
DEV_BYPASS_SECRET = os.getenv('DEV_BYPASS_SECRET', '')
DEV_EMAIL_OTP = os.getenv('DEV_EMAIL_OTP', DEV_BYPASS_VALUE)
USE_TZ = True

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]


# Email — add at the bottom of config/settings.py
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@heartbeatharmony.com')

# Gmail SMTP settings (only used when EMAIL_BACKEND is SMTP)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587') or '587')
EMAIL_USE_TLS = (os.getenv('EMAIL_USE_TLS', 'True') or 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')



# Channels
ASGI_APPLICATION = 'config.asgi.application'

REDIS_URL = os.getenv('REDIS_URL')

if REDIS_URL:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [REDIS_URL],
            },
        }
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        }
    }

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8005').rstrip('/')

# ── S3-compatible media storage (Cloudflare R2 or any S3 endpoint) ──────────
# Set USE_S3=True to activate. All other settings are read from environment
# variables. When USE_S3=False (the default), local filesystem storage is used
# exactly as before — no change to dev or existing deployments.
#
# Env vars (S3_* preferred; R2_* accepted as a backward-compat fallback):
#   USE_S3            — "True" / "False" (default: False)
#   S3_ACCESS_KEY     — R2 / S3 access key ID
#   S3_SECRET_KEY     — R2 / S3 secret access key
#   S3_BUCKET         — bucket name
#   S3_ENDPOINT_URL   — e.g. https://<accountid>.r2.cloudflarestorage.com
#   S3_REGION         — e.g. "auto" for R2 (default: "auto")
#   S3_PUBLIC_URL     — public domain for serving files (pub-xxx.r2.dev or
#                       a custom domain); used as AWS_S3_CUSTOM_DOMAIN so that
#                       file.url returns a full https:// URL, not the raw S3
#                       endpoint URL.

USE_S3 = os.getenv('USE_S3', 'False') == 'True'

if USE_S3:
    # Read S3_* vars, fall back to legacy R2_* names so existing deployments
    # that already have R2_* secrets don't need to be re-keyed immediately.
    AWS_ACCESS_KEY_ID = (
        os.getenv('S3_ACCESS_KEY') or os.getenv('R2_ACCESS_KEY_ID', '')
    )
    AWS_SECRET_ACCESS_KEY = (
        os.getenv('S3_SECRET_KEY') or os.getenv('R2_SECRET_ACCESS_KEY', '')
    )
    AWS_STORAGE_BUCKET_NAME = (
        os.getenv('S3_BUCKET') or os.getenv('R2_BUCKET_NAME', 'hartbeat-harmony-media')
    )
    AWS_S3_ENDPOINT_URL = (
        os.getenv('S3_ENDPOINT_URL') or os.getenv('R2_ENDPOINT_URL', '')
    )
    AWS_S3_REGION_NAME = os.getenv('S3_REGION', 'auto')

    # Strip any http(s):// prefix from the public domain so Django builds
    # clean https:// URLs (S3Boto3Storage prepends "https://" automatically).
    _s3_public_url = (
        os.getenv('S3_PUBLIC_URL') or os.getenv('R2_CUSTOM_DOMAIN', '')
    ).strip()
    AWS_S3_CUSTOM_DOMAIN = (
        _s3_public_url.split('://', 1)[-1] if _s3_public_url else None
    )

    AWS_DEFAULT_ACL = None           # Use bucket policy / public access rules
    AWS_S3_FILE_OVERWRITE = False    # Never silently overwrite existing files

    # Long-lived cache for immutable media assets
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'public, max-age=31536000, immutable',
    }

    # Don't append a query-string auth token — bucket/objects must be public
    AWS_QUERYSTRING_AUTH = False

    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'apps.iap': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'apps.accounts': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}
