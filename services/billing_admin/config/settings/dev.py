from .base import *  # noqa

SECRET_KEY = 'asdadasd'
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
        'NAME': os.getenv('DB_NAME', 'billing_admin'),
        'USER': os.getenv('DB_USERNAME', 'django'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'django'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CHARSET': 'utf-8',
    }
}

AUTH_SERVER = os.getenv('AUTH_SERVER') or 'https://yandexmovies.online/auth2'
AUTH_ENDPOINT = os.getenv('AUTH_ENDPOINT') or f'{AUTH_SERVER}/api/v1/auth/access_check'
AUTH_ADMIN = '6064233@gmail.com'
AUTH_PASSWORD = 'aleks@mail.com'

NOTIFY_SERVER = os.getenv('AUTH_SERVER') or 'https://yandexmovies.online'
NOTIFY_ENDPOINT = os.getenv('NOTIFY_ENDPOINT') or f'{AUTH_SERVER}/notify/api/v1/event'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': os.getenv('DB_NAME', 'billing'),
#         'USER': os.getenv('DB_USERNAME', 'user'),
#         'PASSWORD': os.getenv('DB_PASSWORD', 'useruser'),
#         'HOST': os.getenv('DB_HOST', 'rc1a-7irj22qworosif2n.mdb.yandexcloud.net'),
#         'PORT': os.getenv('DB_PORT', '6432'),
#         'CHARSET': 'utf-8',
#     }
# }
