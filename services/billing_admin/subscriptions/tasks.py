import logging

from config.celery import app
from subscriptions.models import models as subscription_models
from subscriptions.payment_system import models as payment_models

logger = logging.getLogger(__name__)


@app.task(queue="high", timeout=60 * 5, default_retry_delay=10, max_retries=30)
def wait_payment_task(payment_id):
    """Ожидание списания оплаты."""
    payment = subscription_models.PaymentInvoice.objects.filter(id=payment_id).first()
    data = payment.check_payment_status()
    payment.info = data['payment_info']
    status = data['status']

    if status == payment_models.PaymentStatus.UNPAID:
        is_finish = False
    elif status == payment_models.PaymentStatus.PAID:
        payment.set_payed_status()
        is_finish = True
    else:  # failed
        payment.set_cancelled_status()
        is_finish = True

    logger.info(f'wait_payment_task payed: {is_finish}')
    if is_finish:
        payment.subscription.auto_update_status()
    else:
        wait_payment_task.apply_async((payment_id,), countdown=5)


@app.task(queue="high", timeout=60 * 5, default_retry_delay=10, max_retries=3)
def unsubscribe_task(subscription_id):
    """Задача отмены подписки."""
    subscription = subscription_models.Subscription.objects.filter(id=subscription_id).first()
    subscription.process_cancel()


@app.task(queue="default", timeout=60 * 5)
def renew_subscriptions_task():
    """Таска для продления подписок."""
    subscriptions = subscription_models.Subscription.objects.need_renew()

    for subscription in subscriptions:
        subscription.process_renew()


@app.task(queue="default", timeout=60 * 5)
def cancel_expired_subscriptions_task():
    """Таска для отмены истекших подписок."""
    subscriptions = subscription_models.Subscription.objects.need_cancel()

    for subscription in subscriptions:
        subscription.set_cancelled()
