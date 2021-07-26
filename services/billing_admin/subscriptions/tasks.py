from config.celery import app
from django.apps import apps
import logging

LOGGER = logging.getLogger(__name__)


@app.task(queue="high", timeout=60 * 5, default_retry_delay=10, max_retries=30)
def wait_payment_task(payment_id):
    """ожидание списания оплаты"""
    from subscriptions.payment_system.models import PaymentStatus
    payment_model = apps.get_model('subscriptions', 'PaymentInvoice')
    payment = payment_model.objects.filter(id=payment_id).first()

    data = payment.check_payment_status()
    status = data['status']

    if status == PaymentStatus.UNPAID:
        is_finish = False
    elif status == PaymentStatus.PAID:
        payment.set_payed_status()
        is_finish = True
    else:  # failed
        payment.set_cancelled_status()
        is_finish = True

    print(f'wait_payment_task payed: {is_finish}')
    if is_finish:
        payment.info = data['payment_info']
        payment.save()
        payment.subscription.auto_update_status()
    else:
        wait_payment_task.apply_async((payment_id,), countdown=5)


@app.task(queue="high", timeout=60 * 5, default_retry_delay=10, max_retries=3)
def unsubscribe_task(subscription_id):
    from subscriptions.models.models import Subscription

    subscription = Subscription.objects.filter(id=subscription_id).first()
    subscription.process_cancel()


@app.task(queue="default", timeout=60 * 5)
def renew_subscriptions_task():
    """таска для продления подписок"""
    from subscriptions.models.models import Subscription
    subscriptions = Subscription.objects.need_renew()

    for subscription in subscriptions:
        subscription.process_renew()


@app.task(queue="default", timeout=60 * 5)
def cancel_expired_subscriptions_task():
    """таска для отмены истекших подписок"""
    from subscriptions.models.models import Subscription
    subscriptions = Subscription.objects.need_cancel()

    for subscription in subscriptions:
        subscription.set_cancelled()
