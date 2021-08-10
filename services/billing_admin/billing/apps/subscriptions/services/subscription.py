from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING
from uuid import uuid4

import pytz

from billing.apps.subscriptions import models as m
from billing.apps.subscriptions.payment_system.models import SubscribePaymentStatus
from billing.apps.subscriptions.services.client import get_or_create_client
from billing.apps.subscriptions.tasks import wait_payment_task, update_client_roles_task
from billing.services.notify import (
    send_subscription_active_notify,
    send_subscription_cancelled_notify
)

logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from billing.apps.subscriptions.models import Subscription


def subscription_create(user_id, tariff_id, payment_system: str) -> Subscription:
    client = get_or_create_client(user_id)
    subscription = m.Subscription.objects \
        .filter_by_user_id(user_id) \
        .filter_by_status(m.SubscriptionStatus.DRAFT) \
        .first()
    tariff = m.Tariff.objects.get(id=tariff_id)
    if subscription:
        subscription.tariff_id = tariff_id
        subscription.payment_system = m.PaymentSystem(payment_system)
        m.AuditEvents.create(f'user {user_id}', 'update', subscription, subscription.details)
    else:
        subscription = m.Subscription(
            id=uuid4(),
            client=client,
            tariff_id=tariff_id,
            status=m.SubscriptionStatus.DRAFT,
            expiration_date=tariff.next_payment_date(),
            payment_system=m.PaymentSystem(payment_system)
        )
        m.AuditEvents.create(f'user {user_id}', 'create', subscription, subscription.details)
    subscription.payments.all().delete()
    subscription.save()
    return subscription


def subscription_set_active(subscription: Subscription):
    """Делаем подписку активной."""

    subscription.status = m.SubscriptionStatus.ACTIVE
    subscription.expiration_date = subscription.tariff.next_payment_date()
    subscription.save()

    subscription.client.roles_updated = False
    subscription.client.save(update_fields=['roles_updated'])
    update_client_roles_task.apply_async((subscription.client.id,))

    send_subscription_active_notify(
        user_id=subscription.client.user_id,
        description=f'Подписка "{subscription.tariff.product.name}" активирована'
    )


def subscription_set_cancelled(subscription: Subscription):
    """Отмена подписки."""
    subscription.status = m.SubscriptionStatus.CANCELLED
    subscription.save()

    subscription.client.roles_updated = False
    subscription.client.save(update_fields=['roles_updated'])
    update_client_roles_task.apply_async((subscription.client.id,))

    send_subscription_cancelled_notify(
        user_id=subscription.client.user_id,
        description=f'Подписка "{subscription.tariff.product.name}" отменена'
    )


def subscription_set_cancel_at_period_end_status(subscription: Subscription):
    """Делаем подписку отмененной."""
    subscription.status = m.SubscriptionStatus.CANCEL_AT_PERIOD_END
    send_subscription_cancelled_notify(
        user_id=subscription.client.user_id,
        description=f'Подписка "{subscription.tariff.product.name}" отменена'
    )
    subscription.save()


def subscription_prolong_expiration_date(subscription: Subscription):
    """Продлить дату окончания подписки."""
    next_date = subscription.tariff.next_payment_date(subscription.expiration_date)
    subscription.expiration_date = next_date
    subscription.save(action='prolong')


def subscription_process_confirm(subscription: Subscription):
    """
    Процесс подтверждения подписки. Для подтверждения необходимо оплатить подписку.
    Возвращает url на страницу платежной системы.
    """
    data = subscription.payment_system_instance.subscription_create()
    payment = subscription.create_payment(info=data['payment_info'])
    wait_payment_task.apply_async((payment.id,), countdown=5)
    m.AuditEvents.create('system', 'create', payment, payment.details)
    return data['url']


def subscription_define_status_from_payment_system(subscription: Subscription):
    """Определение статуса из платежной системы"""
    status = subscription.payment_system_instance.check_subscription_status()
    return status


def subscription_define_status_from_payment_invoices(subscription: Subscription):
    """Определить статус на основе платежей"""
    last_payment = subscription.payments.filter(status=m.PaymentStatus.PAYED).last()
    if not last_payment:
        return SubscribePaymentStatus.CANCELLED

    payment_to_date = subscription.tariff.next_payment_date(last_payment.created)
    if payment_to_date > datetime.datetime.now(tz=pytz.utc):
        return SubscribePaymentStatus.ACTIVE

    return SubscribePaymentStatus.EXPIRED


def subscription_auto_update_status(subscription: Subscription):
    """Автоматическое определение статуса подписки"""

    if subscription.status in [m.SubscriptionStatus.CANCEL_AT_PERIOD_END]:
        return subscription.status

    status = subscription.define_status_from_payment_system()

    # если нет статуса, то определяем по платежкам из базы
    if not status:
        status = subscription.define_status_from_payment_invoices()

    if status == SubscribePaymentStatus.ACTIVE:
        if subscription.status == m.SubscriptionStatus.ACTIVE:
            subscription.prolong_expiration_date()
        else:
            subscription.set_active()
    elif status == SubscribePaymentStatus.EXPIRED:
        subscription.set_cancelled()
    else:  # failed
        subscription.set_cancelled()

    return status


def subscription_process_cancel(subscription: Subscription):
    """процесс отмены подписки"""
    today = datetime.datetime.now(tz=pytz.utc)
    last_payment = subscription.payments.last()
    cancel_at_period_end = (today - last_payment.created) > datetime.timedelta(days=1)

    if cancel_at_period_end:  # отменяем подписку по окончанию периода
        subscription.set_cancel_at_period_end_status()
    else:  # возвращаем платеж и полностью отменяем подписку
        last_payment.refund_payment()
        subscription.set_cancelled()

    try:
        subscription.payment_system_instance.subscription_cancel(cancel_at_period_end)
    except Exception as e:
        logger.error(e)


def subscription_process_renew(subscription: Subscription):
    """процесс продления подписки."""

    data = subscription.payment_system_instance.subscription_renew()
    if data:
        payment = subscription.create_payment(info=data)
        wait_payment_task.apply_async((payment.id,), countdown=5)
