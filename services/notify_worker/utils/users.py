import psycopg2
import settings
from logger import get_logger
from psycopg2.extras import DictCursor

LOGGER = get_logger(__name__)

GET_ALLOW_CHANNELS = """
SELECT channel.code, notify.code FROM notification_allowchannel
INNER JOIN notification_channel channel on channel.id = notification_allowchannel.channel_id
INNER JOIN notification_client client on client.id = notification_allowchannel.client_id
INNER JOIN notification_notify notify on notify.id = notification_allowchannel.notify_id
WHERE client.user_id = %(user_id)s  AND enabled=true
"""


def get_allow_channels_from_db(user_id: str):
    with psycopg2.connect(**settings.DSN['notify_db']) as _conn, _conn.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(GET_ALLOW_CHANNELS, {'user_id': user_id})
        rows = cursor.fetchall()
        allowed_channels = {}
        for item in rows:
            channel = item[0]
            notify = item[1]

            if notify not in allowed_channels:
                allowed_channels[notify] = []

            allowed_channels[notify].append(channel)
        return allowed_channels
