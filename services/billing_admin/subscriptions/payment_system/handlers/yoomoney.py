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
                "capture": True,
                "description": "Заказ №72",
                "metadata": {
                    'orderNumber': '72'
                },
                "receipt": {
                    "customer": {
                        "full_name": "Ivanov Ivan Ivanovich",
                        "email": "email@email.ru",
                        "phone": "79211234567",
                        "inn": "6321341814"
                    },
                    "items": [
                        {
                            "description": "Переносное зарядное устройство Хувей",
                            "quantity": "1.00",
                            "amount": {
                                "value": 1000,
                                "currency": "RUB"
                            },
                            "vat_code": "2",
                            "payment_mode": "full_payment",
                            "payment_subject": "commodity",
                            "country_of_origin_code": "CN",
                            "product_code": "44 4D 01 00 21 FA 41 00 23 05 41 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 12 00 AB 00",
                            "customs_declaration_number": "10714040/140917/0090376",
                            "excise": "20.00",
                            "supplier": {
                                "name": "string",
                                "phone": "string",
                                "inn": "string"
                            }
                        },
                    ]
                }
            }
        )
        self.logger.info(res)

    def callback(self, *args, **kwargs):
        self.logger.info(args)
        self.logger.info(kwargs)
