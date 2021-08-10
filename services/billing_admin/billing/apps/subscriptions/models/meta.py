from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AccessType(models.TextChoices):
    FREE = 'free', _('бесплатный доступ')
    STANDARD = 'standard', _('обычная подписка')
    EXTRA = 'extra', _('расширенная подписка')


class PaymentSystem(models.TextChoices):
    """Платежные системы, например YooKassa, robokassa, и т.д."""
    YOOMONEY = settings.YOOMONEY, _("Платежная система Юмани")
    STRIPE = settings.STRIPE, _("Платежная система Stripe")


class SubscriptionPeriods(models.TextChoices):
    """Периоды списания средств."""
    MONTHLY = "per month", _("каждый месяц")
    YEARLY = "per year", _("каждый год")


class SubscriptionStatus(models.TextChoices):
    """Статусы подписок."""
    DRAFT = "draft", _("На оформлении")
    INACTIVE = "inactive", _("Не активная")
    ACTIVE = "active", _("Активная")
    EXPIRED = "expired", _("Истек срок действия")
    CANCELLED = "cancelled", _("Подписка отменена")
    CANCEL_AT_PERIOD_END = "cancel_at_period_end", _("Отмена после окончания периода")

    @classmethod
    @property
    def active_statuses(cls):
        return [cls.ACTIVE, cls.CANCEL_AT_PERIOD_END]


class PaymentStatus(models.TextChoices):
    """Статусы платежей."""
    NOT_PAYED = "not_payed", _("Не оплачен")
    PAYED = "payed", _("Оплачен")
    PENDING = "pending", _("Ждем подтверждения оплаты")
    FAILED = "failed", _("Оплата не успешна")
    CANCELLED = "cancelled", _("Оплата отменена")
    REFUNDED = "refunded", _("Выполнен возврат")
