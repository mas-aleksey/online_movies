import json
from subscriptions.payment_system.payment_factory import AbstractPaymentSystem
from django.conf import settings
from yookassa import Configuration, Payment


CONFIG = settings.PAYMENT_SYSTEMS[settings.YOOMONEY]
RETURN_UTL = CONFIG["return_url"]

Configuration.configure(CONFIG["shop_id"], CONFIG["key"])


class YoomoneyPaymentSystem(AbstractPaymentSystem):

    def process_payment(self):
        response = Payment.create(
            {
                "amount": {
                    "value": self.payment.amount,
                    "currency": "RUB"
                },
                "payment_method_data": {
                    "type": "bank_card"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": RETURN_UTL
                },
                "capture": self.payment.amount,
                "description": f"Заказ {self.payment.amount}",
                "save_payment_method": True,
                "metadata": {
                  "order_id": "lalala"
                }
            }
        )
        data = json.loads(response.json())
        self.logger.info(data)
        self.payment.info = data
        self.payment.save()
        return data

    def callback(self, *args, **kwargs):
        self.logger.info(args)
        self.logger.info(kwargs)
