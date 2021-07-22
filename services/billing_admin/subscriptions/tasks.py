from config.celery import app
from django.apps import apps
import logging

LOGGER = logging.getLogger(__name__)


@app.task(queue="high", timeout=60 * 5, default_retry_delay=10, max_retries=30)
def wait_payment_task(payment_id):
    payment_model = apps.get_model('subscriptions', 'PaymentInvoice')
    pay = payment_model.objects.filter(id=payment_id).first()
    is_finish = pay.payment_system_instance.check_payment_status()
    print(f'wait_payment_task payed: {is_finish}')
    if not is_finish:
        wait_payment_task.apply_async((payment_id,), countdown=5)


@app.task(queue="high", timeout=60 * 5, default_retry_delay=10, max_retries=3)
def unsubscribe_task(subscription_id):
    from subscriptions.utils import unsubscribe
    unsubscribe(subscription_id)
