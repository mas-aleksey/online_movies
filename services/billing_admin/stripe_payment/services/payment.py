from stripe_payment.models import SubscriptionInfoDataclass
from stripe_payment.services.price import get_price_id
from stripe_payment.services.stripe_api import create_subscription_checkout_stripe, subscription_retrieve_stripe
from stripe_payment.services.subscription import get_subscription_id


def create_subscription_checkout(subscription: SubscriptionInfoDataclass) -> dict:
    """Создать чек на оплату подписки"""

    price_id = get_price_id(subscription)
    data = create_subscription_checkout_stripe(
        success_url=subscription.success_url,
        cancel_url=subscription.cancel_url,
        price_id=price_id
    )
    return data


def get_subscription_info(billing_subscription_id: str) -> dict:
    """Получить информацию о подписке"""
    stripe_subscription_id = get_subscription_id(billing_subscription_id)

    if not stripe_subscription_id:
        return {}

    data = subscription_retrieve_stripe(stripe_subscription_id)

    return data
