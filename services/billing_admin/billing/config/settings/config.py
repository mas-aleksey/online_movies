import os
from typing import Dict, Union

PAYMENT_RETURN_URL = "https://yandexmovies.online/billing/demo/subscriptions"
YOOMONEY = "yoomoney"

STRIPE = "stripe"
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")

PAYMENT_SYSTEMS: Dict[str, Dict[str, Union[str, bool, None]]] = {
    YOOMONEY: {
        "shop_id": os.environ.get("YOOMONEY_SHOPID"),
        "key": os.environ.get("YOOMONEY_KEY"),
        "active": True,
        "return_url": PAYMENT_RETURN_URL,
    },
    STRIPE: {
        "secret_key": STRIPE_SECRET_KEY,
        "active": True,
        "return_url": PAYMENT_RETURN_URL
    }
}

ACCESS_ROLES_MAPPING = {
    'free': ['free'],
    'standard': ['free', 'standard'],
    'extra': ['free', 'standard', 'extra']
}
