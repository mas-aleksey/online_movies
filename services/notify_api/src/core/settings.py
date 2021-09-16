import os
from logging import config as logging_config
from core.logger import get_logger_config


DEBUG = bool(int(os.getenv('DEBUG', '0')))

MQ_EXCHANGE_NOTIFY = os.getenv('MQ_EXCHANGE_NOTIFY') or 'movies.e.notify'

# Применяем настройки логирования
LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'
LOGGING = get_logger_config(LOG_LEVEL)
logging_config.dictConfig(LOGGING)

HOST = os.getenv('HOST') or '0.0.0.0'
PORT = os.getenv('PORT') or 8000

DNS = {
    'rabbit': {
        'host': os.getenv('RABBIT_HOST') or 'localhost',
        'port': int(os.getenv('RABBIT_PORT', '5672')),
        'login': os.getenv('RABBIT_LOGIN') or 'guest',
        'password': os.getenv('RABBIT_PASSWORD'),
    }
}

DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
