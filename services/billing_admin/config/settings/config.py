import os
from typing import Dict, Union

PAYMENT_RETURN_URL: str = "http//localhost:8000"

YOOMONEY: str = "yoomoney"

PAYMENT_SYSTEMS: Dict[str, Dict[str, Union[str, bool, None]]] = {
    YOOMONEY: {
        "key": os.environ.get("YOOMONEY_KEY"),
        "shop_id": os.environ.get("YOOMONEY_SHOPID"),
        "active": True,
        "return_url": PAYMENT_RETURN_URL,
    }
}