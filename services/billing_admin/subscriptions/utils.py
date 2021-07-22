import datetime
import logging
from typing import Optional
from uuid import uuid4

import pytz

from subscriptions.models.models import (
    Client, Subscription, SubscriptionStatus, PaymentInvoice,
    PaymentSystem
)

LOGGER = logging.getLogger(__name__)


def get_or_create_client(user_id: str) -> Client:
    client = Client.objects.filter(user_id=user_id).first()
    if not client:
        client = Client(id=uuid4(), user_id=user_id)
        client.save()

    return client


def get_subscription_by_client(client: Client, status: SubscriptionStatus) -> Optional[Subscription]:
    return Subscription.objects.filter(client=client, status=status).first()


def create_subscription(user_id, tariff_id) -> Subscription:
    client = get_or_create_client(user_id)
    subscription = get_subscription_by_client(client, SubscriptionStatus.DRAFT)
    if subscription:
        subscription.tariff_id = tariff_id
    else:
        subscription = Subscription(
            id=uuid4(),
            client=client,
            tariff_id=tariff_id,
            status=SubscriptionStatus.DRAFT,
            expiration_date=datetime.datetime.now()
        )
    subscription.save()
    return subscription


def create_payment(subscription: Subscription, payment_system: str):
    amount = subscription.tariff.price
    discount = subscription.discount or subscription.tariff.discount
    if discount:
        amount = round(subscription.tariff.price - (subscription.tariff.price / 100 * discount.value), 2)

    payment = PaymentInvoice(
        id=uuid4(),
        subscription=subscription,
        payment_system=PaymentSystem(payment_system),
        amount=amount
    )
    payment.save()
    return payment


def unsubscribe(subscription_id):
    """процесс отписки"""
    subscription = Subscription.objects.filter(id=subscription_id).first()

    today = datetime.datetime.now(tz=pytz.utc)
    payment = subscription.payments.last()
    cancel_at_period_end = (today - payment.created) > datetime.timedelta(days=1)

    if cancel_at_period_end:  # отменяем подписку по окончанию периода
        subscription.set_cancel_at_period_end_status()
    else:  # возвращаем платеж и полностью отменяем подписку
        payment.refund_payment()
        subscription.set_cancelled_status()

    try:
        payment.payment_system_instance.subscription_cancel(cancel_at_period_end)
    except Exception as e:
        LOGGER.error(e)
