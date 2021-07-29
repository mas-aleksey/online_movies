import logging

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

from billing.apps.subscriptions import models as m
from billing.apps.subscriptions.payment_system.payment_factory import PaymentSystemFactory
from billing.services.notify import (
    send_payment_notify, send_refund_notify
)

logger = logging.getLogger(__name__)


class PaymentInvoice(TimeStampedModel, m.AuditMixin):
    """История оплат."""
    id = models.UUIDField(primary_key=True)
    subscription = models.ForeignKey(
        m.Subscription,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="подписка"
    )
    amount = models.FloatField(_('конечная цена'), validators=[MinValueValidator(0)])
    info = models.JSONField(_('информация о платеже'), blank=True, null=True)
    status = models.CharField(
        _("Статус платежа"),
        max_length=64,
        choices=m.PaymentStatus.choices,
        default=m.PaymentStatus.NOT_PAYED
    )
    payment_system = models.CharField(
        _("Тип платежной системы"),
        max_length=64,
        choices=m.PaymentSystem.choices,
        default=m.PaymentSystem.YOOMONEY
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
        self.status = m.PaymentStatus.PAYED
        send_payment_notify(
            user_id=self.subscription.client.user_id,
            amount=self.amount,
            description=f'Продление подписки "{self.subscription.tariff.product.name}"'
        )
        self.save()

    def set_cancelled_status(self):
        """Тут логика при отмене платежа."""
        self.status = m.PaymentStatus.CANCELLED
        self.save()

    def set_refunded_status(self):
        """Тут логика при отмене платежа."""
        self.status = m.PaymentStatus.REFUNDED
        send_refund_notify(
            user_id=self.subscription.client.user_id,
            amount=self.amount,
            description=f'Возврат средств по подписке "{self.subscription.tariff.product.name}"'
        )
        self.save()

    def refund_payment(self):
        """Тут логика для возврата платежа."""
        if self.status == m.PaymentStatus.PAYED:
            self.payment_system_instance.refund_payment()
            self.set_refunded_status()

