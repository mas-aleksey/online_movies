"""Gunicorn config file."""

import os
from multiprocessing import cpu_count

settings: dict = {
    'project_name': 'app',
    'worker_class': 'sync',
    'project_path': os.environ.get('PROJECT_PATH', '.'),
    'host': os.environ.get('APP_HOST', '0.0.0.0'),
    'port': os.environ.get('APP_PORT', '8080'),
    'log_level': os.environ.get('LOG_LEVEL', 'INFO'),
    'worker_numbers': os.environ.get('WORKER_NUMBERS'),
    'pythonpath': os.environ.get('PYTHONPATH'),
}


def get_workers_count(default=1):
    """Get number of workers."""
    try:
        n = cpu_count()
    except NotImplementedError:
        n = default
    return n + 1


if settings['worker_numbers']:
    workers = int(settings['worker_numbers'])
else:
    workers = get_workers_count()

if settings['pythonpath']:
    pythonpath = settings['pythonpath']

worker_class = settings['worker_class']
bind = '{host}:{port}'.format(**settings)
backlog = 2048
keepalive = 75
timeout = 300
max_requests = 0
limit_request_line = 8190
chdir = settings['project_path']
daemon = False
errorlog = '-'
preload_app = True
loglevel = settings['log_level'].lower()
proc_name = settings['project_name']
raw_env = [
    'LOG_LEVEL={log_level}'.format(**settings),
]
