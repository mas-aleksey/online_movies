from .base import *  # noqa

SECRET_KEY = 'asdasd'
DEBUG = True  # type: ignore
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INSTALLED_APPS += [
    'debug_toolbar',
]
# BROKER_URL = 'amqp://guest:guest@localhost:5672/'
# BROKER_URL = 'redis://127.0.0.1:6379/0'
# CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'

INTERNAL_IPS = ['127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME', 'notify_admin'),
        'USER': os.getenv('DB_USERNAME', 'django'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CHARSET': 'utf-8',
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME', 'notify'),
        'USER': os.getenv('DB_USERNAME', 'user'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'rc1a-7irj22qworosif2n.mdb.yandexcloud.net'),
        'PORT': os.getenv('DB_PORT', '6432'),
        'CHARSET': 'utf-8',
    }
}
