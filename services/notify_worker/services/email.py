from logger import get_logger
from models import Channel, EventMessage
from services.base import BaseWorker
from utils.smtp import sendmail
from utils.templates import render_template

LOGGER = get_logger(__name__)


class EmailMessageWorker(BaseWorker):
    """Воркер для отправки email сообщения."""

    channel = Channel.email

    def __init__(self, message: EventMessage) -> None:
        super().__init__(message)
        self.payload = self.message.payload
        self.notice = self.message.name

    def send(self, user):
        context = {'username': user.username, **self.payload}
        subject_template = render_template(self.template.short_text, context)
        body_template = render_template(self.template.message, context)

        sendmail(to=user.email, subject=subject_template, body_html=body_template)

    def process(self):
        for user in self.message.users:
            if not user.has_allowed_channel(self.notice, self.channel):
                LOGGER.info(f'Пользователь отключил уведомление по {self.channel} для {self.notice}')
                continue

            self.send(user)
