from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from billing.apps.subscriptions import models as m
from billing.services.notify import (
    send_payment_notify, send_refund_notify
)

if TYPE_CHECKING:
    from billing.apps.subscriptions.models import Subscription


def create_payment(subscription: Subscription, info=None):
    """Создать платеж для подписки."""
    payment = m.PaymentInvoice(
        id=uuid4(),
        subscription=subscription,
        payment_system=m.PaymentSystem(subscription.payment_system),
        amount=subscription.amount,
        status=m.PaymentStatus.PENDING,
        info=info
    )
    payment.save()
    return payment


def invoice_set_payed_status(payment_invoice: m.PaymentInvoice):
    """Тт логика при получении подтверждения об оплате."""
    payment_invoice.status = m.PaymentStatus.PAYED
    send_payment_notify(
        user_id=payment_invoice.subscription.client.user_id,
        amount=payment_invoice.amount,
        description=f'Продление подписки "{payment_invoice.subscription.tariff.product.name}"'
    )
    payment_invoice.save()


def invoice_set_cancelled_status(payment_invoice: m.PaymentInvoice):
    """Тут логика при отмене платежа."""
    payment_invoice.status = m.PaymentStatus.CANCELLED
    payment_invoice.save()


def invoice_set_refunded_status(payment_invoice: m.PaymentInvoice):
    """Тут логика при отмене платежа."""
    payment_invoice.status = m.PaymentStatus.REFUNDED
    send_refund_notify(
        user_id=payment_invoice.subscription.client.user_id,
        amount=payment_invoice.amount,
        description=f'Возврат средств по подписке "{payment_invoice.subscription.tariff.product.name}"'
    )
    payment_invoice.save()


def invoice_refund_payment(payment_invoice: m.PaymentInvoice):
    """Тут логика для возврата платежа."""
    if payment_invoice.status == m.PaymentStatus.PAYED:
        payment_invoice.payment_system_instance.refund_payment()
        payment_invoice.set_refunded_status()
