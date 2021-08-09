import datetime
import logging

import pytz
from django.conf import settings
from django.db import models
from django.db.models import QuerySet, Manager
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel, SoftDeletableModel
from celery.result import AsyncResult
from billing.config.celery import app

from billing.apps.subscriptions import models as m
from billing.apps.subscriptions.payment_system.payment_factory import PaymentSystemFactory
from billing.apps.subscriptions.services.payment import create_payment
from billing.apps.subscriptions.services.subscription import (
    subscription_set_active, subscription_set_cancelled,
    subscription_set_cancel_at_period_end_status, subscription_process_confirm,
    subscription_define_status_from_payment_system, subscription_define_status_from_payment_invoices,
    subscription_auto_update_status, subscription_process_cancel, subscription_process_renew,
    subscription_prolong_expiration_date
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


class Subscription(TimeStampedModel, SoftDeletableModel, m.AuditMixin):
    """Подписка."""
    id = models.UUIDField(primary_key=True)
    client = models.ForeignKey(m.Client, on_delete=models.CASCADE, verbose_name="клиент")
    expiration_date = models.DateField(_("дата окончания"), blank=True, null=True)
    tariff = models.ForeignKey(m.Tariff, on_delete=models.DO_NOTHING, verbose_name="тариф")
    discount = models.ForeignKey(m.Discount, on_delete=models.DO_NOTHING, verbose_name="скидка", blank=True, null=True)
    wait_payment_task = models.UUIDField(_("id задачи на оплату"), blank=True, null=True, default=None)
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

    @property
    def payment_task_status(self):
        if not self.wait_payment_task:
            return None
        res = AsyncResult(str(self.wait_payment_task), app=app)
        return res.state

    def set_active(self):
        """Делаем подписку активной."""
        subscription_set_active(self)

    def set_cancelled(self):
        """Отмена подписки."""
        subscription_set_cancelled(self)

    def set_cancel_at_period_end_status(self):
        """Делаем подписку отмененной."""
        subscription_set_cancel_at_period_end_status(self)

    def prolong_expiration_date(self):
        """Продлить дату окончания подписки."""
        subscription_prolong_expiration_date(self)

    def create_payment(self, info=None):
        """Создать платеж для подписки."""
        return create_payment(self, info)

    def process_confirm(self):
        """
        Процесс подтверждения подписки. Для подтверждения необходимо оплатить подписку.
        Возвращает url на страницу платежной системы.
        """
        return subscription_process_confirm(self)

    def define_status_from_payment_system(self):
        """Определение статуса из платежной системы"""
        return subscription_define_status_from_payment_system(self)

    def define_status_from_payment_invoices(self):
        """Определить статус на основе платежей"""

        return subscription_define_status_from_payment_invoices(self)

    def auto_update_status(self):
        """Автоматическое определение статуса подписки"""
        return subscription_auto_update_status(self)

    def process_cancel(self):
        """процесс отмены подписки"""
        subscription_process_cancel(self)

    def process_renew(self):
        """процесс продления подписки."""

        subscription_process_renew(self)
