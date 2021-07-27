import datetime

import settings


def send_notify(client, name, payload, user_id, notify_type="immediately", channels=None):
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

    r = client.post(f'{settings.NOTIFY_BASE_URL}/api/v1/event', json=data,
                    headers={'content-type': 'application/json'})
    return r.text


def send_payment_notify(client, user_id, amount, description):
    """Отправка уведомления об оплате"""
    name = 'success_payment'
    payload = {
        "subject": "Списание средств",
        "amount": amount,
        "description": description,
    }
    return send_notify(client, name=name, payload=payload, user_id=user_id)
