import os
from logging import config as logging_config

from core.logger import get_logger_config

DEBUG = bool(int(os.getenv('DEBUG', '0')))

# Применяем настройки логирования
LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'
LOGGING = get_logger_config(LOG_LEVEL)
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

# Настройки Redis
REDIS_HOST = os.getenv('REDIS_HOST') or 'localhost'
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))

# Настройки Elasticsearch
ELASTIC_HOST = os.getenv('ELASTIC_HOST', 'localhost')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', '9200'))

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ELASTIC_MOVIES_INDEX = 'movies'
ELASTIC_GENRE_INDEX = 'genre'
ELASTIC_PERSON_INDEX = 'person'

CACHE_EXPIRE_TIME_IN_SECONDS = 60 * 5