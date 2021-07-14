import os

from kombu import Queue, Exchange

from .base import TIME_ZONE

ENDPOINT = os.getenv('YMQ_ENDPOINT', '')
CELERY_BROKER_URL = 'sqs://{}'.format(ENDPOINT)
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'is_secure': True,
}

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
    'debug_task': {
        "task": 'config.celery.debug_task',
        "schedule": 10.0
    }
}
