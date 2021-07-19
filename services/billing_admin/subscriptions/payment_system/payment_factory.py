from typing import Dict, Type
from subscriptions.models import PaymentSystem, PaymentInvoice
from subscriptions.payment_system.payment_system import AbstractPaymentSystem
from subscriptions.payment_system.handlers import (
    YoomoneyPaymentSystem
)


class PaymentSystemFactory:

    payment_systems: Dict[str, Type[AbstractPaymentSystem]] = {
        PaymentSystem.YOOMONEY.value: YoomoneyPaymentSystem,
    }

    @classmethod
    def get_payment_system(cls, payment: PaymentInvoice) -> AbstractPaymentSystem:
        payment_system_class = cls.payment_systems[payment.payment_system]
        return payment_system_class(payment)
