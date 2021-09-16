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
RABBIT_PASSWORD = os.getenv('RABBIT_PASSWORD')

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


def split_task_to_timezones(
        task_name: str, func: str,
        minute='*', hour='*', day_of_week='*', day_of_month='*', month_of_year='*',
        args: list = None
) -> dict:
    """
    Создает запланированные задачи с учетом таймзоны.
    Задача будет выполнена в указанное время для каждой таймзоны.
    @param task_name: наименование задачи
    @param func: функция для выполнения
    @param args: список аргументов, для передачи в функцию через запятую
    список параметров для crontab: minute, hour, day_of_week, day_of_month, month_of_year
    @return: словарь с задачами для scheduler

    """
    if args is None:
        args = []
    tasks = {}
    for timezone in pytz.all_timezones_set:
        nowfun = partial(datetime.datetime.now, tz=pytz.timezone(timezone))

        task_args = (timezone, *args)
        tasks[f"{task_name}_{timezone.replace('/', '_')}"] = {
            "task": func,
            "schedule": crontab(
                minute=minute,
                hour=hour,
                day_of_week=day_of_week,
                day_of_month=day_of_month,
                month_of_year=month_of_year,
                nowfun=nowfun
            ),
            "args": task_args
        }

    return tasks


CELERY_BEAT_SCHEDULE = {
    **split_task_to_timezones(
        task_name="new_movies",
        func='notification.tasks.new_movies_task',
        hour='20',  # каждую пятницу в 20 часов
        day_of_week='5'
    )
}
