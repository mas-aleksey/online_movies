import datetime
import os
from functools import partial

import pytz
from celery.schedules import crontab
from kombu import Queue, Exchange

from .base import TIME_ZONE

RABBIT_HOST = os.getenv('RABBIT_HOST') or 'localhost'
RABBIT_PORT = int(os.getenv('RABBIT_PORT', '5672'))
RABBIT_LOGIN = os.getenv('RABBIT_LOGIN') or 'guest'
RABBIT_PASSWORD = os.getenv('RABBIT_PASSWORD') or 'test12'

CELERY_BROKER_URL = f'amqp://{RABBIT_LOGIN}:{RABBIT_PASSWORD}@{RABBIT_HOST}:{RABBIT_PORT}/'

CELERY_ACCEPT_CONTENT = {"json"}
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True  # отображать запущенные задачи в админке

CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = (
    Queue('low', Exchange('low'), routing_key='low'),
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('high', Exchange('high'), routing_key='high'),
)

CELERY_BEAT_SCHEDULE = {

}
