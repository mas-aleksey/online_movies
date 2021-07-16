from subscriptions.payment_system.payment_factory import AbstractPaymentSystem
from django.conf import settings
from yookassa import Configuration, Payment


CONFIG = settings.PAYMENT_SYSTEMS[settings.YOOMONEY]
RETURN_UTL = CONFIG["return_url"]

Configuration.configure(CONFIG["shop_id"], CONFIG["key"])


class YoomoneyPaymentSystem(AbstractPaymentSystem):

    def process_payment(self):
        res = Payment.create(
            {
                "amount": {
                    "value": self.payment.amount,
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": RETURN_UTL
                },
                "capture": self.payment.amount,
                "description": f"Заказ {self.payment.amount}",
                "metadata": {
                  "order_id": "lalala"
                }
            }
        )
        self.logger.info(res)
        return res

    def callback(self, *args, **kwargs):
        self.logger.info(args)
        self.logger.info(kwargs)
