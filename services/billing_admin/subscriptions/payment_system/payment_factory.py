from django.conf import settings
from typing import Dict, Type
from subscriptions.payment_system.payment_system import AbstractPaymentSystem
from subscriptions.payment_system.handlers import YoomoneyPaymentSystem


class PaymentSystemFactory:

    payment_systems: Dict[str, Type[AbstractPaymentSystem]] = {
        settings.YOOMONEY: YoomoneyPaymentSystem,
    }

    @classmethod
    def get_payment_system(cls, payment) -> AbstractPaymentSystem:
        payment_system_class = cls.payment_systems[payment.payment_system]
        return payment_system_class(payment)
