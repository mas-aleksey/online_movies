from typing import Optional

from stripe_payment.models import StripeId, ObjectType


def create_or_update_subscription_id(billing_subscription_id: str, stripe_subscription_id: str) -> None:
    """Сохранить или обновить информацию о подписке."""

    subscription = StripeId.objects.subscriptions().filter(
        billing_id=billing_subscription_id
    ).last()

    if subscription:
        subscription.stripe_id = stripe_subscription_id
        subscription.save()
        return

    StripeId.objects.create(
        stripe_id=stripe_subscription_id,
        billing_id=billing_subscription_id,
        object_type=ObjectType.SUBSCRIPTION
    )


def get_subscription_id(billing_subscription_id: str) -> Optional[str]:
    """Получить id подписки."""
    subscription = StripeId.objects.subscriptions().filter(
        billing_id=billing_subscription_id
    ).last()

    if subscription:
        return subscription.stripe_id

    return None
