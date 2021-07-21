import dataclasses

from django.db import models
from model_utils.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _

from stripe_payment.managers import StripeIdManager


@dataclasses.dataclass
class SubscriptionInfoDataclass:
    product_id: str
    product_name: str
    tariff_id: str
    tariff_period: str
    amount: int
    success_url: str
    cancel_url: str


class ObjectType(models.TextChoices):
    PRICE = 'price'
    PRODUCT = 'product'
    SUBSCRIPTION = 'subscription'


class StripeId(TimeStampedModel):
    """ Сопоставление id в Stripe """
    stripe_id = models.CharField(_("id в stripe"), max_length=250)
    billing_id = models.CharField(_("id в billing"), max_length=250)
    object_type = models.CharField(_("Тип объекта"), max_length=64, choices=ObjectType.choices)

    objects = StripeIdManager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('цены')
        verbose_name_plural = _('цена')

    def __str__(self):
        return f'{self.stripe_id} {self.billing_id}'
