import abc
import importlib
from typing import Optional, Type

import settings
from logger import get_logger
from models import EventMessage, TemplateMessage
from utils.templates import get_template_from_db

LOGGER = get_logger(__name__)


class BaseWorker:
    """Базовый воркер обработки сообщения из очереди."""
    message: EventMessage
    template: TemplateMessage

    def __init__(self, message: EventMessage) -> None:
        self.message = message
        self.template = get_template_from_db(message.name)

    @abc.abstractmethod
    def process(self):
        raise NotImplemented


def get_worker_class(path: str = None) -> Optional[Type[BaseWorker]]:
    """Импортирует класс из строчки"""

    if not path:
        return None
    mod_name, func_name = path.rsplit('.', 1)
    mod = importlib.import_module(mod_name)
    func = getattr(mod, func_name)
    return func


def on_base_callback(chan, method_frame, header_frame, body):
    """Callback вызываемый при получении сообщения из RabbitMQ."""

    message = EventMessage.parse_raw(body)
    for channel in message.channels:
        class_name = settings.HANDLERS.get(channel)

        if not class_name:
            LOGGER.exception(f'Не найден обработчик {channel} для события {message.name}')
            continue

        worker_class = get_worker_class(class_name)
        worker = worker_class(message=message)
        worker.process()

    chan.basic_ack(delivery_tag=method_frame.delivery_tag)
