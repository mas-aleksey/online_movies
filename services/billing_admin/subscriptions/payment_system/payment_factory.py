from typing import Dict, Type
from django.apps import apps
from subscriptions.payment_system.payment_system import AbstractPaymentSystem
from subscriptions.payment_system.handlers import (
    YoomoneyPaymentSystem
)

PaymentSystem = apps.get_model('subscriptions', 'PaymentSystem')
PaymentInvoice = apps.get_model('subscriptions', 'PaymentInvoice')


class PaymentSystemFactory:

    payment_systems: Dict[str, Type[AbstractPaymentSystem]] = {
        PaymentSystem.YOOMONEY.value: YoomoneyPaymentSystem,
    }

    @classmethod
    def get_payment_system(cls, payment: PaymentInvoice) -> AbstractPaymentSystem:
        payment_system_class = cls.payment_systems[payment.payment_system]
        return payment_system_class(payment)
