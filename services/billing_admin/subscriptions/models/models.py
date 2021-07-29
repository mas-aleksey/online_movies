import datetime
from datetime import date
from uuid import uuid4

import pytz
from dateutil.relativedelta import relativedelta
from django.core.validators import MinValueValidator
from django.db import models
from django.forms.models import model_to_dict
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel, SoftDeletableModel

from services.notify import (
    send_payment_notify, send_refund_notify, send_subscription_active_notify,
    send_subscription_cancelled_notify
)
from subscriptions.models.meta import (
    PaymentStatus, PaymentSystem, AccessType, SubscriptionStatus, SubscriptionPeriods
)
from services.auth import add_auth_user_role, delete_auth_user_role
from subscriptions.payment_system.models import SubscribePaymentStatus
from subscriptions.payment_system.payment_factory import PaymentSystemFactory
from subscriptions.querysets import SubscriptionQuerySet
from subscriptions.tasks import wait_payment_task

import logging

logger = logging.getLogger(__name__)


class Client(TimeStampedModel):
    """Пользователи кинотеатра."""
    id = models.UUIDField(primary_key=True)
    user_id = models.UUIDField(_('uuid пользователя'), unique=True)

    class Meta:
        verbose_name = _('клиент')
        verbose_name_plural = _('клиенты')

    def __str__(self):
        return str(self.user_id)


class Product(TimeStampedModel):
    """Продукты (подписки)."""
    id = models.UUIDField(primary_key=True)
    name = models.CharField(_('название'), unique=True, max_length=50)
    description = models.TextField(_('описание'), blank=True, null=True)
    access_type = models.CharField(
        _("Тип доступа к фильмам"),
        max_length=64,
        choices=AccessType.choices,
        default=AccessType.FREE
    )

    class Meta:
        verbose_name = _('продукт')
        verbose_name_plural = _('продукты')

    def __str__(self):
        return self.name


class Discount(TimeStampedModel):
    """Скидки."""
    id = models.UUIDField(primary_key=True)
    name = models.CharField(_('название'), unique=True, max_length=50)
    code = models.CharField(_('промокод'), max_length=50, blank=True, null=True)
    description = models.TextField(_('описание'), blank=True, null=True)
    value = models.FloatField(_('размер скидки'), validators=[MinValueValidator(0)])
    is_active = models.BooleanField(_('активная скидка'), default=True)

    class Meta:
        verbose_name = _('скидка')
        verbose_name_plural = _('скидки')

    def __str__(self):
        return f'{self.name} {self.value}'


class Tariff(TimeStampedModel):
    """Тарифные планы подписок."""
    id = models.UUIDField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='продукт', related_name='tariffs')
    discount = models.ForeignKey(Discount, on_delete=models.DO_NOTHING, verbose_name="скидка", blank=True, null=True)
    price = models.FloatField(_('цена'), validators=[MinValueValidator(0)])
    period = models.CharField(
        _("Период списания"),
        max_length=64,
        choices=SubscriptionPeriods.choices,
        default=SubscriptionPeriods.MONTHLY
    )

    class Meta:
        ordering = ['-id']
        verbose_name = _('тариф')
        verbose_name_plural = _('тарифы')

    def __str__(self):
        return f'{self.product} {self.price} {self.period}'

    def next_payment_date(self, today: date = None) -> date:
        if not today:
            today = date.today()
        if self.period == SubscriptionPeriods.MONTHLY:
            delta = relativedelta(months=+1)
        elif self.period == SubscriptionPeriods.YEARLY:
            delta = relativedelta(years=+1)
        else:
            raise ValueError(f"unknown period: {self.period}")

        return today + delta


class AuditMixin(models.Model):
    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, action=None):
        super().save(force_insert, force_update, using, update_fields)
        status = action or getattr(self, 'status', 'something')
        AuditEvents.create('models', status, self.__class__.__name__, self.id, self.details)

    @property
    def details(self) -> str:
        return str(model_to_dict(self))


class Subscription(TimeStampedModel, SoftDeletableModel, AuditMixin):
    """Подписка."""
    id = models.UUIDField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="клиент")
    expiration_date = models.DateField(_("дата окончания"), blank=True, null=True)
    tariff = models.ForeignKey(Tariff, on_delete=models.DO_NOTHING, verbose_name="тариф")
    discount = models.ForeignKey(Discount, on_delete=models.DO_NOTHING, verbose_name="скидка", blank=True, null=True)
    status = models.CharField(
        _("Статус подписки"),
        max_length=64,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.INACTIVE,
    )
    payment_system = models.CharField(
        _("Тип платежной системы"),
        max_length=64,
        choices=PaymentSystem.choices,
        default=PaymentSystem.YOOMONEY
    )
    objects = SubscriptionQuerySet.as_manager()

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

    def set_active(self):
        """Делаем подписку активной."""
        roles = settings.ACCESS_ROLES_MAPPING[self.tariff.product.access_type]
        add_auth_user_role(self.client.user_id, roles)
        send_subscription_active_notify(
            user_id=self.client.user_id,
            description=f'Подписка "{self.tariff.product.name}" активирована'
        )
        AuditEvents.create('system', f'granted: {roles}', 'user', self.client.user_id, self.details)
        self.status = SubscriptionStatus.ACTIVE
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
        AuditEvents.create('system', f'deleted: {roles}', 'user', self.client.user_id, self.details)
        self.status = SubscriptionStatus.CANCELLED
        self.save()

    def set_cancel_at_period_end_status(self):
        """Делаем подписку отмененной."""
        self.status = SubscriptionStatus.CANCEL_AT_PERIOD_END
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
        payment = PaymentInvoice(
            id=uuid4(),
            subscription=self,
            payment_system=PaymentSystem(self.payment_system),
            amount=self.amount,
            status=PaymentStatus.PENDING,
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
        AuditEvents.create('system', 'create', 'wait_payment_task', payment.id, payment.details)
        return data['url']

    def define_status_from_payment_system(self):
        """Определение статуса из платежной системы"""
        status = self.payment_system_instance.check_subscription_status()
        return status

    def define_status_from_payment_invoices(self):
        """Определить статус на основе платежей"""
        last_payment = self.payments.filter(status=PaymentStatus.PAYED).last()
        if not last_payment:
            return SubscribePaymentStatus.CANCELLED

        payment_to_date = self.tariff.next_payment_date(last_payment.created)
        if payment_to_date > datetime.datetime.now(tz=pytz.utc):
            return SubscribePaymentStatus.ACTIVE

        return SubscribePaymentStatus.EXPIRED

    def auto_update_status(self):
        """Автоматическое определение статуса подписки"""

        if self.status in [SubscriptionStatus.CANCEL_AT_PERIOD_END]:
            return self.status

        status = self.define_status_from_payment_system()

        # если нет статуса, то определяем по платежкам из базы
        if not status:
            status = self.define_status_from_payment_invoices()

        if status == SubscribePaymentStatus.ACTIVE:
            if self.status == SubscriptionStatus.ACTIVE:
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


class PaymentInvoice(TimeStampedModel, AuditMixin):
    """История оплат."""
    id = models.UUIDField(primary_key=True)
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="подписка"
    )
    amount = models.FloatField(_('конечная цена'), validators=[MinValueValidator(0)])
    info = models.JSONField(_('информация о платеже'), blank=True, null=True)
    status = models.CharField(
        _("Статус платежа"),
        max_length=64,
        choices=PaymentStatus.choices,
        default=PaymentStatus.NOT_PAYED
    )
    payment_system = models.CharField(
        _("Тип платежной системы"),
        max_length=64,
        choices=PaymentSystem.choices,
        default=PaymentSystem.YOOMONEY
    )

    class Meta:
        verbose_name = _('платеж')
        verbose_name_plural = _('платежи')

    def __str__(self):
        return f'{self.subscription} {self.amount} {self.status}'

    @property
    def payment_system_instance(self):
        tariff = self.subscription.tariff
        last_payment_info = self.info if self.info else {}
        data = {
            'payment_system': self.payment_system,
            'subscription_id': str(self.subscription.id),
            'last_payment': last_payment_info,
            'product_id': str(tariff.product.id),
            'product_name': tariff.product.name,
            'tariff_id': str(tariff.id),
            'tariff_period': tariff.period,
            'amount': self.amount,
            'success_url': self.subscription.return_url,
            'cancel_url': self.subscription.return_url
        }
        return PaymentSystemFactory.get_payment_system(**data)

    def check_payment_status(self):
        """проверка статуса платежа в платежной системе."""
        status = self.payment_system_instance.check_payment_status()
        return status

    def set_payed_status(self):
        """Тт логика при получении подтверждения об оплате."""
        self.status = PaymentStatus.PAYED
        send_payment_notify(
            user_id=self.subscription.client.user_id,
            amount=self.amount,
            description=f'Продление подписки "{self.subscription.tariff.product.name}"'
        )
        self.save()

    def set_cancelled_status(self):
        """Тут логика при отмене платежа."""
        self.status = PaymentStatus.CANCELLED
        self.save()

    def set_refunded_status(self):
        """Тут логика при отмене платежа."""
        self.status = PaymentStatus.REFUNDED
        send_refund_notify(
            user_id=self.subscription.client.user_id,
            amount=self.amount,
            description=f'Возврат средств по подписке "{self.subscription.tariff.product.name}"'
        )
        self.save()

    def refund_payment(self):
        """Тут логика для возврата платежа."""
        if self.status == PaymentStatus.PAYED:
            self.payment_system_instance.refund_payment()
            self.set_refunded_status()


class AuditEvents(TimeStampedModel):
    """История событий."""
    who = models.CharField(_("Инициатор события"), max_length=50)
    what = models.CharField(_("Событие"), max_length=50)
    related_name = models.CharField(_("Объект"), max_length=50)
    related_id = models.CharField(_("Id объекта"), max_length=50)
    details = models.TextField(_("Подробности"), blank=True, null=True)

    class Meta:
        verbose_name = _('событие')
        verbose_name_plural = _('события')

    @classmethod
    def create(cls, who, what, related_name, related_id, details=None) -> None:
        logger.info('%s %s %s %s %s', who, what, related_name, related_id, details)
        cls(who=who, what=what, related_name=related_name, related_id=related_id, details=details).save()
