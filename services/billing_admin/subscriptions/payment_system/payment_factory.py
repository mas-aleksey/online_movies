from __future__ import annotations

from typing import Dict, Type, TYPE_CHECKING

from django.conf import settings

from subscriptions.payment_system.handlers import YoomoneyPaymentSystem, StripePaymentSystem

if TYPE_CHECKING:
    from subscriptions.payment_system.payment_system import AbstractPaymentSystem


class PaymentSystemFactory:

    payment_systems: Dict[str, Type[AbstractPaymentSystem]] = {
        settings.YOOMONEY: YoomoneyPaymentSystem,
        settings.STRIPE: StripePaymentSystem,
    }

    @classmethod
    def get_payment_system(cls, payment) -> AbstractPaymentSystem:
        payment_system_class = cls.payment_systems[payment.payment_system]
        return payment_system_class(payment)
