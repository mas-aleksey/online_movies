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
CELERY_RESULT_BACKEND = 'django-db'

CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = (
    Queue('low', Exchange('low'), routing_key='low'),
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('high', Exchange('high'), routing_key='high'),
)

CELERY_BEAT_SCHEDULE = {
    'renew_subscriptions_task': {
        "task": 'billing.apps.subscriptions.tasks.renew_subscriptions_task',  # продление подписок
        "schedule": 60.0  # каждые 60 сек
    },
    'cancel_expired_subscriptions_task': {
        "task": 'billing.apps.subscriptions.tasks.cancel_expired_subscriptions_task', # отмена истекших подписок
        "schedule": 60.0  # каждые 60 сек
    }
}
