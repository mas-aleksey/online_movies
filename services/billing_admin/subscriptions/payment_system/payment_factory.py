from typing import Dict, Type
from subscriptions.models import PaymentSystem, PaymentHistory
from subscriptions.payment_system.payment_system import AbstractPaymentSystem
from subscriptions.payment_system.handlers import (
    YoomoneyPaymentSystem, DummyPaymentSystem
)


class PaymentSystemFactory:

    payment_systems: Dict[str, Type[AbstractPaymentSystem]] = {
        PaymentSystem.DUMMY.value: DummyPaymentSystem,
        PaymentSystem.YOOMONEY.value: YoomoneyPaymentSystem,
    }

    @classmethod
    def get_payment_system(cls, payment: PaymentHistory) -> AbstractPaymentSystem:
        system = payment.subscription.payment_system
        payment_system_class = cls.payment_systems[system]
        return payment_system_class(payment)
