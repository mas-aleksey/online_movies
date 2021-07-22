from stripe_payment.models import SubscriptionInfoDataclass
from stripe_payment.services.price import get_price_id
from stripe_payment.services.stripe_api import create_subscription_checkout_stripe, subscription_retrieve_stripe, \
    subscription_cancel_stripe, subscription_delete_stripe, invoice_retrieve_stripe, payment_refund_stripe
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


def subscription_refund(billing_subscription_id: str):
    """Возврат последнего платежа по подписке"""
    stripe_subscription_id = get_subscription_id(billing_subscription_id)
    data = subscription_retrieve_stripe(stripe_subscription_id)
    invoice_id = data['latest_invoice']
    if not invoice_id:
        return

    data = invoice_retrieve_stripe(invoice_id)
    payment_intent_id = data['payment_intent']
    if not payment_intent_id:
        return

    data = payment_refund_stripe(payment_intent_id)
    return data


def subscription_cancel(billing_subscription_id: str, cancel_at_period_end=False) -> dict:
    """Отмена подписки."""
    stripe_subscription_id = get_subscription_id(billing_subscription_id)
    if cancel_at_period_end:
        data = subscription_cancel_stripe(stripe_subscription_id)
    else:
        data = subscription_delete_stripe(stripe_subscription_id)
    return data
