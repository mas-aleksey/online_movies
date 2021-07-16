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

GET_USER_INFO_SQL = """
select email, username from users
where id = %(user_id)s
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


def get_user_info_from_auth(user_id: str):
    """вернуть информацию о пользователе из auth"""
    with psycopg2.connect(**settings.DSN['auth_db']) as _conn, _conn.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(GET_USER_INFO_SQL, {'user_id': user_id})
        rows = cursor.fetchall()
        user_info = {
            'email': None,
            'username': None
        }
        if not rows:
            return user_info

        user_info['email'] = rows[0][0]
        user_info['username'] = rows[0][1]

        return user_info
