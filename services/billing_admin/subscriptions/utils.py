from uuid import uuid4, UUID
from subscriptions.models import (
    Client, Tariff, Subscription, SubscriptionStatus, PaymentInvoice,
    PaymentSystem, PaymentStatus
)

def get_or_create_client(user_id: str) -> Client:
    client = Client.objects.filter(user_id=user_id).first()
    if not client:
        client = Client(id=uuid4(), user_id=UUID(user_id))
        client.save()

    return client

def get_tariff_by_id(tariff_id) -> Tariff:
    return Tariff.objects.filter(id=tariff_id).first()


def create_subscription(user_id, tariff_id) -> Subscription:
    client = get_or_create_client(user_id)
    tariff = get_tariff_by_id(tariff_id)
    subscription = Subscription(
        id=uuid4(),
        client=client,
        tariff=tariff,
        status=SubscriptionStatus.DRAFT
    )
    subscription.save()
    return subscription

def create_payment(subscription: Subscription, payment_system: str, amount: float):
    payment = PaymentInvoice(
        id=uuid4(),
        subscription=subscription,
        payment_system=PaymentSystem(payment_system),
        amount=amount
    )
    payment.save()
    return payment
