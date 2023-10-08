import logging

from django.apps import apps

from billing.config.celery import app
from . import models as m
from . import services
from .payment_system import models as payment_models

logger = logging.getLogger(__name__)


@app.task(queue="high", timeout=60 * 5, default_retry_delay=10, max_retries=30)
def wait_payment_task(payment_id):
    """Ожидание списания оплаты."""
    payment = m.PaymentInvoice.objects.get(id=payment_id)
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
    subscription = m.Subscription.objects.filter(id=subscription_id).first()
    subscription.process_cancel()


@app.task(queue="default", timeout=60 * 5)
def renew_subscriptions_task():
    """Таска для продления подписок."""
    subscriptions = m.Subscription.objects.need_renew()

    for subscription in subscriptions:
        subscription.process_renew()


@app.task(queue="default", timeout=60 * 5)
def cancel_expired_subscriptions_task():
    """Таска для отмены истекших подписок."""
    subscriptions = m.Subscription.objects.need_cancel()

    for subscription in subscriptions:
        subscription.set_cancelled()


@app.task(queue="low", timeout=60 * 5)
def audit_create_task(who, what, instance_app_label, instance_class, instance_id, details=None) -> None:
    model = apps.get_model(instance_app_label, instance_class)
    instance = model.objects.get(pk=instance_id)
    logger.info('%s %s %s %s %s', who, what, instance_class, instance_id, details)
    m.AuditEvents(who=who, what=what, content_object=instance, details=details).save()


@app.task(queue="high", timeout=60 * 5)
def update_client_roles_task(client_id) -> None:
    """Обновить роли пользователя в auth."""
    services.client.set_auth_client_roles(client_id)


@app.task(queue="low", timeout=60 * 60)
def update_clients_roles_task() -> None:
    """Обновить роли всех не обновленных пользователей в auth."""
    clients = m.Client.objects.filter(roles_updated=False)
    for client in clients:
        update_client_roles_task.apply_async((client.id,))
