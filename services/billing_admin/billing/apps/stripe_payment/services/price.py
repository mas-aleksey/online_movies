from billing.apps.stripe_payment.models import SubscriptionInfoDataclass, StripeId, ObjectType
from billing.apps.stripe_payment.services.product import get_product_id
from billing.apps.stripe_payment.services.stripe_api import create_price_stripe


def get_price_id(subscription: SubscriptionInfoDataclass) -> str:
    """Возвращает id цены в stripe."""
    billing_price_id = subscription.tariff_id
    price = StripeId.objects.prices().filter(billing_id=billing_price_id).first()
    if price:
        return price.stripe_id

    product_id = get_product_id(subscription.product_id, subscription.product_name)
    stripe_price_id = create_price_stripe(
        amount=subscription.amount,
        interval=subscription.tariff_period,
        product_id=product_id
    )
    StripeId.objects.create(stripe_id=stripe_price_id, billing_id=billing_price_id, object_type=ObjectType.PRICE)

    return stripe_price_id

