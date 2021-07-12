import psycopg2
from jinja2 import Template
from psycopg2.extras import DictCursor

import settings
from logger import get_logger
from models import TemplateMessage

LOGGER = get_logger(__name__)


def get_template_from_db(name: str) -> TemplateMessage:
    with psycopg2.connect(**settings.DSN['notify_db']) as _conn, _conn.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(f'SELECT short_text, message FROM notify_template WHERE title=\'{name}\'')
        rows = cursor.fetchall()
        if not rows:
            raise Exception(f'Не найден шаблон для события {name}')
        template = TemplateMessage.parse_obj(rows[0])
        return template


def render_template(body: str, context: dict) -> str:
    template = Template(body)
    return template.render(**context)
