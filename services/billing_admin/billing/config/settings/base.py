import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', '')
DEBUG = os.getenv('DEBUG', False)
ALLOWED_HOSTS = [os.getenv('ALLOWED_HOSTS', '*')]
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.postgres",
    "psqlextra",

    'rest_framework',
    'django_celery_results',
    'django_celery_beat',

    'billing.apps.subscriptions',
    'billing.apps.stripe_payment',

    'demo'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'billing.services.middleware.AuthenticationMiddleware'
]

ROOT_URLCONF = 'billing.config.urls'

TEMPLATES = [
    {
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
    },
]

WSGI_APPLICATION = 'billing.config.wsgi.application'

DATABASES = {
    'default': {
        "ENGINE": "psqlextra.backend",
        'NAME': os.getenv('DB_NAME') or 'billing',
        'USER': os.getenv('DB_USERNAME') or 'postgres',
        'PASSWORD': os.getenv('DB_PASSWORD') or 'QWEasd123',
        'HOST': os.getenv('DB_HOST') or 'localhost',
        'PORT': os.getenv('DB_PORT') or 5432,
        'CHARSET': 'utf-8',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(process)d %(thread)d %(name)s:%(lineno)s %(funcName)s() %(message)s'
        },
        'verbose_sql': {
            'format': '%(levelname)s %(asctime)s %(process)d %(thread)d %(name)s:%(lineno)s %(funcName)s() %(sql)s\n%(params)s\n%(duration)ss'
        },
    },
    'handlers': {
        'real_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'real_console_sql': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose_sql',
        },
        'console': {
            'class': 'logging.handlers.MemoryHandler',
            'target': 'real_console',
            'capacity': 8192,
        },
        'console_sql': {
            'class': 'logging.handlers.MemoryHandler',
            'target': 'real_console_sql',
            'capacity': 8192,
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console_sql'],
            'level': 'WARNING',
            'propagate': False,
        },
        'boto': {
            'level': 'WARNING',
        },
        'requests': {
            'level': 'WARNING',
        },
        'meridian': {
            'level': 'DEBUG',
        },
        'celery': {
            'level': 'WARNING',
        },
        'south': {
            'level': 'INFO',
        },
        'py.warnings': {
            'level': 'ERROR',  # change to WARNING to show DeprecationWarnings, etc.
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/billing-admin/'

# Проверка доступа
ASYNC_SERVER = os.getenv('ASYNC_SERVER') or 'https://yandexmovies.online/async'
AUTH_SERVER = os.getenv('AUTH_SERVER') or 'http://movies_auth:5000/auth2'
AUTH_ENDPOINT = os.getenv('AUTH_ENDPOINT') or f'{AUTH_SERVER}/api/v1/auth/access_check'
AUTH_ADMIN = os.getenv('AUTH_ADMIN') or f'admin'
AUTH_PASSWORD = os.getenv('AUTH_PASSWORD') or f'pwd'

# Нотификации
NOTIFY_SERVER = os.getenv('NOTIFY_SERVER') or 'http://notify_api:8000/notify'
NOTIFY_ENDPOINT = os.getenv('NOTIFY_ENDPOINT') or f'{NOTIFY_SERVER}/api/v1/event'

from .celery import *  # noqa
from .config import *  # noqa
