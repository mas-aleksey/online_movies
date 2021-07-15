import datetime

import requests
from django.conf import settings


def send_notify(data):
    requests.post(settings.NOTIFY_ENDPOINT, data=data)


def send_payment_notify(user_id, email, amount, description):
    """Отправка уведомления об оплате"""
    data = {
        "name": "success_payment",
        "type": "immediately",
        "payload": {
            "subject": "Списание средств",
            "amount": amount,
            "description": description,
        },
        "channels": [
            "email"
        ],
        "users": [
            {
                "user_id": user_id,
                "email": email,
                "username": "aleks",
                "timezone": "string"
            }
        ],
        "timestamp": datetime.datetime.now()
    }
    send_notify(data)
