import datetime

import requests
from django.conf import settings


def send_notify(data):
    r = requests.post(settings.NOTIFY_ENDPOINT, json=data, headers={'content-type': 'application/json'})
    return r.text


def send_payment_notify(user_id, amount, description):
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
                "user_id": user_id
            }
        ],
        "timestamp": str(datetime.datetime.now())
    }
    return send_notify(data)