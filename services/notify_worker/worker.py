import backoff
import pika

import settings
from logger import get_logger
from services.base import on_base_callback

LOGGER = get_logger(__name__)


def get_connection():
    """Создает подключение к RabbitMQ."""
    credentials = pika.PlainCredentials(
        username=settings.DSN['rabbit']['login'],
        password=settings.DSN['rabbit']['password']
    )
    parameters = pika.ConnectionParameters(
        host=settings.DSN['rabbit']['host'],
        port=settings.DSN['rabbit']['port'],
        credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    return connection


@backoff.on_exception(backoff.expo, (Exception,))
def main():
    connection = get_connection()
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(settings.MQ_QUEUE, on_base_callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    connection.close()


if __name__ == '__main__':
    main()
