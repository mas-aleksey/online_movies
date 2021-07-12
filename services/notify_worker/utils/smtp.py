import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import settings
from logger import get_logger

LOGGER = get_logger(__name__)


def sendmail(to: str, subject: str, body_html: str) -> None:
    LOGGER.info(f'send mail {to=} {subject=}')

    sender_email = settings.EMAIL_SENDER
    password = settings.EMAIL_PASSWORD
    smtp_server = settings.EMAIL_SERVER
    smtp_port = settings.EMAIL_PORT

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to

    html = MIMEText(body_html, "html")
    message.attach(html)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo_or_helo_if_needed()
        server.starttls()
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, to, message.as_string())
