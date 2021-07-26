import datetime

import requests
from django.conf import settings


def send_notify(name, payload, user_id, notify_type="immediately", channels=None):
    if channels is None:
        channels = ["email"]

    data = {
        "name": name,
        "type": notify_type,
        "payload": payload,
        "channels": channels,
        "users": [
            {
                "user_id": str(user_id)
            }
        ],
        "timestamp": str(datetime.datetime.now())
    }

    r = requests.post(settings.NOTIFY_ENDPOINT, json=data, headers={'content-type': 'application/json'})
    print(settings.NOTIFY_ENDPOINT, r.text)
    return r.text


def send_payment_notify(user_id, amount, description):
    """Отправка уведомления об оплате"""
    name = 'success_payment'
    payload = {
        "subject": "Списание средств",
        "amount": amount,
        "description": description,
    }
    return send_notify(name=name, payload=payload, user_id=user_id)


def send_refund_notify(user_id, amount, description):
    """Отправка уведомления об возврате"""
    name = 'refund_payment'
    payload = {
        "subject": "Возврат средств",
        "amount": amount,
        "description": description,
    }
    return send_notify(name=name, payload=payload, user_id=user_id)


def send_subscription_active_notify(user_id, description):
    """Отправка уведомления об активации подписки"""
    name = 'subscription_active'
    payload = {
        "subject": "Активация подписки",
        "description": description,
    }
    return send_notify(name=name, payload=payload, user_id=user_id)


def send_subscription_cancelled_notify(user_id, description):
    """Отправка уведомления об активации подписки"""
    name = 'subscription_cancelled'
    payload = {
        "subject": "Отмена подписки",
        "description": description,
    }
    return send_notify(name=name, payload=payload, user_id=user_id)
