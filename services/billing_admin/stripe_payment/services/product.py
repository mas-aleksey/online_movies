from stripe_payment.models import StripeId, ObjectType
from stripe_payment.services.stripe_api import get_or_create_product_stripe


def get_product_id(billing_product_id: str, name: str) -> str:
    """Возвращает id продукта в stripe."""

    product = StripeId.objects.products().filter(billing_id=billing_product_id).first()
    if product:
        return product.stripe_id

    stripe_product_id = get_or_create_product_stripe(product_id=billing_product_id, name=name)
    StripeId.objects.create(stripe_id=stripe_product_id, billing_id=billing_product_id, object_type=ObjectType.PRODUCT)

    return stripe_product_id
