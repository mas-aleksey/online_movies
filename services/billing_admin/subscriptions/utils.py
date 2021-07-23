import logging
from typing import Optional
from uuid import uuid4

from subscriptions.models.models import (
    Client, Subscription, SubscriptionStatus, PaymentInvoice,
    PaymentSystem, Tariff
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


def create_subscription(user_id, tariff_id, payment_system: str) -> Subscription:
    client = get_or_create_client(user_id)
    subscription = Subscription.objects.filter_by_user_id(user_id).filter_by_status(SubscriptionStatus.DRAFT).first()
    tariff = Tariff.objects.get(id=tariff_id)
    if subscription:
        subscription.tariff_id = tariff_id
    else:
        subscription = Subscription(
            id=uuid4(),
            client=client,
            tariff_id=tariff_id,
            status=SubscriptionStatus.DRAFT,
            expiration_date=tariff.next_payment_date(),
            payment_system=PaymentSystem(payment_system)
        )
    subscription.save()
    return subscription


def create_payment(subscription: Subscription):
    amount = subscription.tariff.price
    discount = subscription.discount or subscription.tariff.discount
    if discount:
        amount = round(subscription.tariff.price - (subscription.tariff.price / 100 * discount.value), 2)

    payment = PaymentInvoice(
        id=uuid4(),
        subscription=subscription,
        payment_system=PaymentSystem(subscription.payment_system),
        amount=amount
    )
    payment.save()
    return payment
