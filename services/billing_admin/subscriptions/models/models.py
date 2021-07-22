from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel, SoftDeletableModel

from subscriptions.models.meta import (
    PaymentStatus, PaymentSystem, AccessType, SubscriptionStatus, SubscriptionPeriods
)
from services.auth import add_auth_user_role, delete_auth_user_role
from subscriptions.payment_system.payment_factory import PaymentSystemFactory
from subscriptions.querysets import SubscriptionQuerySet


class Client(TimeStampedModel):
    """ Пользователи кинотеатра """
    id = models.UUIDField(primary_key=True)
    user_id = models.UUIDField(_('uuid пользователя'), unique=True)

    class Meta:
        verbose_name = _('клиент')
        verbose_name_plural = _('клиенты')

    def __str__(self):
        return str(self.user_id)


class Product(TimeStampedModel):
    """ Продукты (подписки) """
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
    """ Скидки """
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
    """ Тарифные планы подписок """
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

    @property
    def next_payment_date(self) -> date:
        if self.period == SubscriptionPeriods.MONTHLY:
            delta = relativedelta(months=+1)
        elif self.period == SubscriptionPeriods.YEARLY:
            delta = relativedelta(years=+1)
        else:
            raise ValueError(f"unknown period: {self.period}")

        return date.today() + delta


class Subscription(TimeStampedModel, SoftDeletableModel):
    """ Подписка """
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
    objects = SubscriptionQuerySet.as_manager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('подписка')
        verbose_name_plural = _('подписки')

    def __str__(self):
        return f'{self.client} {self.tariff} {self.status}'

    def set_active(self):
        """ делаем подписку активной """
        roles = settings.ACCESS_ROLES_MAPPING[self.tariff.product.access_type]
        add_auth_user_role(self.client.user_id, roles)
        self.status = SubscriptionStatus.ACTIVE
        self.expiration_date = self.tariff.next_payment_date
        self.save()

    def set_cancelled_status(self):
        """ отмена подписки """
        roles = settings.ACCESS_ROLES_MAPPING[self.tariff.product.access_type]
        delete_auth_user_role(self.client.user_id, roles)
        self.status = SubscriptionStatus.CANCELLED
        self.save()

    def set_cancel_at_period_end_status(self):
        """ делаем подписку отмененной """
        self.status = SubscriptionStatus.CANCEL_AT_PERIOD_END
        self.save()


class PaymentInvoice(TimeStampedModel):
    """ История оплат """
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
        return PaymentSystemFactory.get_payment_system(self)

    def set_payed_status(self):
        """ тут логика при получении подтверждения об оплате """
        self.status = PaymentStatus.PAYED
        self.save()

    def set_cancelled_status(self):
        """ тут логика при отмене платежа """
        self.status = PaymentStatus.CANCELLED
        self.save()

    def set_refunded_status(self):
        """ тут логика при отмене платежа """
        self.status = PaymentStatus.REFUNDED
        self.save()

    def refund_payment(self):
        """ тут логика для возврата платежа """
        if self.status == PaymentStatus.PAYED:
            self.payment_system_instance.refund_payment()
            self.set_refunded_status()
