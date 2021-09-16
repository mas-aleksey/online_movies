import logging
import requests

LOGGER = logging.getLogger(__name__)


def send_event_to_notify_api(message: dict):
    r = requests.post(url='http://localhost:8000/api/v1/event', json=message)
    r.raise_for_status()


def get_new_movies(timezone):
    """Получить данные о новых фильмах"""
    # todo тут должен быть запрос к БД
    test_data = {
        "name": "new_movies",
        "type": "scheduled",
        "payload": {
            "films": [
                {
                    "name": "Операция Ы",
                    "description": "Пересмотрите обязательно!"
                },
                {
                    "name": "Миссия невыполнима",
                    "description": "Увлекательный боевик!"
                },
            ]
        },
        "channels": [
            "email",
        ],
        "users": [
            {
                "user_id": "string",
                "username": "aleks",
                "email": "user1@gmail.com",
                "timezone": "Asia/Irkutsk",
                "allowed_channels": {
                    "new_movies": [
                        "email", "sms"
                    ]
                }
            },
            {
                "user_id": "string",
                "username": "petr",
                "email": "user2@gmail.com",
                "timezone": "Africa/Tripoli",
                "allowed_channels": {
                    "new_movies": [
                        "email", "sms"
                    ]
                }
            }
        ],
        "timestamp": "2021-06-19 02:53:58.937874"
    }
    test_data["users"] = [
        user
        for user in test_data["users"]
        if user["timezone"] == timezone
    ]
    return test_data
