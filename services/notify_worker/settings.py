import os

DEBUG = bool(int(os.getenv('DEBUG', '0')))
MQ_QUEUE = os.getenv('MQ_QUEUE') or 'movies.q.notify_fast'

DSN = {
    'rabbit': {
        'host': os.getenv('RABBIT_HOST') or 'localhost',
        'port': int(os.getenv('RABBIT_PORT', '5672')),
        'login': os.getenv('RABBIT_LOGIN') or 'guest',
        'password': os.getenv('RABBIT_PASSWORD') or 'test12',
    },
    'notify_db': {
        'host': os.getenv('DB_HOST') or 'localhost',
        'port': os.getenv('DB_PORT') or 5432,
        'dbname': os.getenv('DB_NAME') or 'postgres',
        'user': os.getenv('DB_USERNAME') or 'postgres',
        'password': os.getenv('DB_PASSWORD') or 'test12',
    },
    'auth_db': {
        'host': os.getenv('AUTH_DB_HOST') or 'localhost',
        'port': os.getenv('AUTH_DB_PORT') or 5432,
        'dbname': os.getenv('AUTH_DB_NAME') or 'postgres',
        'user': os.getenv('AUTH_DB_USERNAME') or 'postgres',
        'password': os.getenv('AUTH_DB_PASSWORD') or 'test12',
    },
}

EMAIL_SENDER = os.getenv('EMAIL_SENDER') or 'user@yandex.ru'
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD') or 'password'
EMAIL_SERVER = os.getenv('EMAIL_SERVER') or 'smtp.yandex.ru'
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))

# Обработчики событий
HANDLERS = {
    'email': 'services.email.EmailMessageWorker'
}
