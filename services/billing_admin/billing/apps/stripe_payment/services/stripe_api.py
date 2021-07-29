import stripe

from django.conf import settings
from stripe.error import InvalidRequestError

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_or_create_product_stripe(product_id: str, name: str) -> str:
    """Создает продукт в stripe."""

    try:
        product = stripe.Product.retrieve(product_id)
    except InvalidRequestError:
        product = stripe.Product.create(
            name=name,
            id=product_id
        )

    return product['id']


def create_price_stripe(amount: int, interval: str, product_id: str) -> str:
    """Создать цену в stripe."""

    price = stripe.Price.create(
        unit_amount=amount,
        currency="rub",
        recurring={"interval": interval},
        product=product_id,
    )

    return price['id']


def create_subscription_checkout_stripe(success_url: str, cancel_url: str, price_id: str) -> dict:
    """Создать чек на оплату подписки."""

    response = stripe.checkout.Session.create(
        success_url=success_url,
        cancel_url=cancel_url,
        payment_method_types=['card'],
        mode='subscription',
        line_items=[{'price': price_id, 'quantity': 1}]
    )
    return response


def checkout_retrieve_stripe(checkout_id: str) -> dict:
    """Информация об оплате."""

    response = stripe.checkout.Session.retrieve(checkout_id)
    return response


def subscription_retrieve_stripe(subscription_id: str) -> dict:
    """Информация о подписке."""

    response = stripe.Subscription.retrieve(subscription_id)
    return response


def subscription_cancel_stripe(subscription_id: str) -> dict:
    """Отмена подписки."""
    response = stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)
    return response


def subscription_delete_stripe(subscription_id: str) -> dict:
    """Удаление подписки."""
    response = stripe.Subscription.delete(subscription_id)
    return response


def invoice_retrieve_stripe(invoice_id: str) -> dict:
    """Получить информацию о счете."""

    response = stripe.Invoice.retrieve(invoice_id)
    return response


def payment_refund_stripe(payment_intent_id: str):
    """Вернуть платеж."""

    response = stripe.Refund.create(payment_intent=payment_intent_id)
    return response
