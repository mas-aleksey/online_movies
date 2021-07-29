import datetime
import logging
from uuid import uuid4

import pytz
from django.conf import settings
from django.db import models
from django.db.models import QuerySet, Manager
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel, SoftDeletableModel

from billing.apps.subscriptions import models as m
from billing.apps.subscriptions.payment_system.models import SubscribePaymentStatus
from billing.apps.subscriptions.payment_system.payment_factory import PaymentSystemFactory
from billing.apps.subscriptions.tasks import wait_payment_task
from billing.services.auth import add_auth_user_role, delete_auth_user_role
from billing.services.notify import (
    send_subscription_active_notify,
    send_subscription_cancelled_notify
)

logger = logging.getLogger(__name__)


class SubscriptionQuerySet(QuerySet):
    def exclude_cancelled(self):
        statuses = [
            m.SubscriptionStatus.INACTIVE,
            m.SubscriptionStatus.CANCELLED,
        ]
        qs = self.exclude(status__in=statuses)
        return qs

    def filter_by_user_id(self, user_id: str):
        return self.filter(client__user_id=user_id)

    def filter_by_status(self, status):
        return self.filter(status=status)

    def need_renew(self):
        """Подписки, которые необходимо продлить."""

        statuses = [
            m.SubscriptionStatus.ACTIVE,
            m.SubscriptionStatus.EXPIRED,
        ]
        today = datetime.datetime.now(tz=pytz.utc)
        return self.filter(expiration_date__lte=today, status__in=statuses)

    def need_cancel(self):
        """Подписки, которые необходимо отменить."""
        statuses = [
            m.SubscriptionStatus.CANCEL_AT_PERIOD_END,
        ]
        today = datetime.datetime.now(tz=pytz.utc)
        return self.filter(expiration_date__lte=today, status__in=statuses)


class SubscriptionServiceMixin:
    @property
    def amount(self):
        tariff = self.tariff
        amount = tariff.price
        discount = self.discount or tariff.discount
        if discount:
            amount = round(tariff.price - (tariff.price / 100 * discount.value), 2)
        return amount

    @property
    def return_url(self):
        config = settings.PAYMENT_SYSTEMS[self.payment_system]
        return_utl = config["return_url"]
        return f'{return_utl}/{self.id}?refresh_page=1'

    @property
    def payment_system_instance(self):
        tariff = self.tariff
        last_payment = self.payments.last()
        last_payment_info = last_payment.info if last_payment else {}
        data = {
            'payment_system': self.payment_system,
            'subscription_id': str(self.id),
            'last_payment': last_payment_info,
            'product_id': str(tariff.product.id),
            'product_name': tariff.product.name,
            'tariff_id': str(tariff.id),
            'tariff_period': tariff.period,
            'amount': self.amount,
            'success_url': self.return_url,
            'cancel_url': self.return_url
        }
        return PaymentSystemFactory.get_payment_system(**data)

    def set_active(self):
        """Делаем подписку активной."""
        roles = settings.ACCESS_ROLES_MAPPING[self.tariff.product.access_type]
        add_auth_user_role(self.client.user_id, roles)
        send_subscription_active_notify(
            user_id=self.client.user_id,
            description=f'Подписка "{self.tariff.product.name}" активирована'
        )
        m.AuditEvents.create('system', f'granted: {roles}', self.client, self.details)
        self.status = m.SubscriptionStatus.ACTIVE
        self.expiration_date = self.tariff.next_payment_date()
        self.save()

    def set_cancelled(self):
        """Отмена подписки."""
        roles = settings.ACCESS_ROLES_MAPPING[self.tariff.product.access_type]
        delete_auth_user_role(self.client.user_id, roles)
        send_subscription_cancelled_notify(
            user_id=self.client.user_id,
            description=f'Подписка "{self.tariff.product.name}" отменена'
        )
        m.AuditEvents.create('system', f'deleted: {roles}', self.client, self.details)
        self.status = m.SubscriptionStatus.CANCELLED
        self.save()

    def set_cancel_at_period_end_status(self):
        """Делаем подписку отмененной."""
        self.status = m.SubscriptionStatus.CANCEL_AT_PERIOD_END
        send_subscription_cancelled_notify(
            user_id=self.client.user_id,
            description=f'Подписка "{self.tariff.product.name}" отменена'
        )
        self.save()

    def prolong_expiration_date(self):
        """Продлить дату окончания подписки."""
        next_date = self.tariff.next_payment_date(self.expiration_date)
        self.expiration_date = next_date
        self.save(action='prolong')

    def create_payment(self, info=None):
        """Создать платеж для подписки."""
        payment = m.PaymentInvoice(
            id=uuid4(),
            subscription=self,
            payment_system=m.PaymentSystem(self.payment_system),
            amount=self.amount,
            status=m.PaymentStatus.PENDING,
            info=info
        )
        payment.save()
        return payment

    def process_confirm(self):
        """
        Процесс подтверждения подписки. Для подтверждения необходимо оплатить подписку.
        Возвращает url на страницу платежной системы.
        """
        data = self.payment_system_instance.subscription_create()
        payment = self.create_payment(info=data['payment_info'])
        wait_payment_task.apply_async((payment.id,), countdown=5)
        m.AuditEvents.create('system', 'create', payment, payment.details)
        return data['url']

    def define_status_from_payment_system(self):
        """Определение статуса из платежной системы"""
        status = self.payment_system_instance.check_subscription_status()
        return status

    def define_status_from_payment_invoices(self):
        """Определить статус на основе платежей"""
        last_payment = self.payments.filter(status=m.PaymentStatus.PAYED).last()
        if not last_payment:
            return SubscribePaymentStatus.CANCELLED

        payment_to_date = self.tariff.next_payment_date(last_payment.created)
        if payment_to_date > datetime.datetime.now(tz=pytz.utc):
            return SubscribePaymentStatus.ACTIVE

        return SubscribePaymentStatus.EXPIRED

    def auto_update_status(self):
        """Автоматическое определение статуса подписки"""

        if self.status in [m.SubscriptionStatus.CANCEL_AT_PERIOD_END]:
            return self.status

        status = self.define_status_from_payment_system()

        # если нет статуса, то определяем по платежкам из базы
        if not status:
            status = self.define_status_from_payment_invoices()

        if status == SubscribePaymentStatus.ACTIVE:
            if self.status == m.SubscriptionStatus.ACTIVE:
                self.prolong_expiration_date()
            else:
                self.set_active()
        elif status == SubscribePaymentStatus.EXPIRED:
            self.set_cancelled()
        else:  # failed
            self.set_cancelled()

        return status

    def process_cancel(self):
        """процесс отмены подписки"""
        today = datetime.datetime.now(tz=pytz.utc)
        last_payment = self.payments.last()
        cancel_at_period_end = (today - last_payment.created) > datetime.timedelta(days=1)

        if cancel_at_period_end:  # отменяем подписку по окончанию периода
            self.set_cancel_at_period_end_status()
        else:  # возвращаем платеж и полностью отменяем подписку
            last_payment.refund_payment()
            self.set_cancelled()

        try:
            self.payment_system_instance.subscription_cancel(cancel_at_period_end)
        except Exception as e:
            logger.error(e)

    def process_renew(self):
        """процесс продления подписки."""

        data = self.payment_system_instance.subscription_renew()
        if data:
            payment = self.create_payment(info=data)
            wait_payment_task.apply_async((payment.id,), countdown=5)


class Subscription(TimeStampedModel, SoftDeletableModel, m.AuditMixin, SubscriptionServiceMixin):
    """Подписка."""
    id = models.UUIDField(primary_key=True)
    client = models.ForeignKey(m.Client, on_delete=models.CASCADE, verbose_name="клиент")
    expiration_date = models.DateField(_("дата окончания"), blank=True, null=True)
    tariff = models.ForeignKey(m.Tariff, on_delete=models.DO_NOTHING, verbose_name="тариф")
    discount = models.ForeignKey(m.Discount, on_delete=models.DO_NOTHING, verbose_name="скидка", blank=True, null=True)
    status = models.CharField(
        _("Статус подписки"),
        max_length=64,
        choices=m.SubscriptionStatus.choices,
        default=m.SubscriptionStatus.INACTIVE,
    )
    payment_system = models.CharField(
        _("Тип платежной системы"),
        max_length=64,
        choices=m.PaymentSystem.choices,
        default=m.PaymentSystem.YOOMONEY
    )
    objects = Manager.from_queryset(SubscriptionQuerySet)()

    class Meta:
        ordering = ['-id']
        verbose_name = _('подписка')
        verbose_name_plural = _('подписки')

    def __str__(self):
        return f'{self.client} {self.tariff} {self.status}'
