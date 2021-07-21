import os
from typing import Dict, Union

PAYMENT_RETURN_URL = "https://yandexmovies.online/billing/demo/subscriptions"
YOOMONEY = "yoomoney"
STRIPE = "stripe"

PAYMENT_SYSTEMS: Dict[str, Dict[str, Union[str, bool, None]]] = {
    YOOMONEY: {
        "shop_id": os.environ.get("YOOMONEY_SHOPID"),
        "key": os.environ.get("YOOMONEY_KEY"),
        "active": True,
        "return_url": PAYMENT_RETURN_URL,
    },
    STRIPE: {
        "secret_key": os.environ.get("STRIPE_SECRET_KEY"),
        "active": True,
        "return_url": PAYMENT_RETURN_URL
    }
}
