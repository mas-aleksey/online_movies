from config.celery import app

from notification.services import send_event_to_notify_api, get_new_movies


@app.task(queue="default", timeout=60 * 10)
def new_movies_task(timezone: str, *args, **kwargs):
    """Задача для отправки уведомлений о новых фильмах."""

    data = get_new_movies(timezone)
    send_event_to_notify_api(data)
