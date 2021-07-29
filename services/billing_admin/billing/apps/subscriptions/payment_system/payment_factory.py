from __future__ import annotations
from typing import Dict, Type, TYPE_CHECKING
from django.conf import settings
from billing.apps.subscriptions.payment_system.handlers import YoomoneyPaymentSystem, StripePaymentSystem

if TYPE_CHECKING:
    from billing.apps.subscriptions.payment_system.payment_system import AbstractPaymentSystem


class PaymentSystemFactory:
    payment_systems: Dict[str, Type[AbstractPaymentSystem]] = {
        settings.YOOMONEY: YoomoneyPaymentSystem,
        settings.STRIPE: StripePaymentSystem,
    }

    @classmethod
    def get_payment_system(
            cls, payment_system: str, last_payment: dict,
            subscription_id: str, product_id: str, product_name: str,
            tariff_id: str, tariff_period: str, amount: float,
            success_url: str, cancel_url: str
    ) -> AbstractPaymentSystem:
        payment_system_class = cls.payment_systems[payment_system]
        instance = payment_system_class(
            subscription_id=subscription_id,
            last_payment=last_payment,
            product_id=product_id,
            product_name=product_name,
            tariff_id=tariff_id,
            tariff_period=tariff_period,
            amount=amount,
            success_url=success_url,
            cancel_url=cancel_url
        )
        return instance
