import logging
from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

from . import (
    AccessType, SubscriptionPeriods
)

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






