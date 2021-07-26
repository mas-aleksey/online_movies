
from typing import Optional
from uuid import uuid4

from subscriptions.models.models import (
    Client, Subscription, SubscriptionStatus, PaymentSystem, Tariff, AuditEvents
)


def get_or_create_client(user_id: str) -> Client:
    client = Client.objects.filter(user_id=user_id).first()
    if not client:
        client = Client(id=uuid4(), user_id=user_id)
        client.save()
        AuditEvents.create('system', 'create', 'user', client.user_id)
    return client


def get_subscription_by_client(client: Client, status: SubscriptionStatus) -> Optional[Subscription]:
    return Subscription.objects.filter(client=client, status=status).first()


def create_subscription(user_id, tariff_id, payment_system: str) -> Subscription:
    client = get_or_create_client(user_id)
    subscription = Subscription.objects.filter_by_user_id(user_id).filter_by_status(SubscriptionStatus.DRAFT).first()
    tariff = Tariff.objects.get(id=tariff_id)
    if subscription:
        subscription.tariff_id = tariff_id
        subscription.payment_system = PaymentSystem(payment_system)
        AuditEvents.create(f'user {user_id}', 'update', 'subscription', subscription.id, subscription.details)
    else:
        subscription = Subscription(
            id=uuid4(),
            client=client,
            tariff_id=tariff_id,
            status=SubscriptionStatus.DRAFT,
            expiration_date=tariff.next_payment_date(),
            payment_system=PaymentSystem(payment_system)
        )
        AuditEvents.create(f'user {user_id}', 'create', 'subscription', subscription.id, subscription.details)
    subscription.payments.all().delete()
    subscription.save()
    return subscription
