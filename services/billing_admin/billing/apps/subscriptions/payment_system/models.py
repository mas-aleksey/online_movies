from enum import Enum


class SubscribePaymentStatus(Enum):
    """Статусы подписки, возвращаемые из платежной системы."""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PaymentStatus(Enum):
    """Статусы платежей, возвращаемые из платежной системы."""
    PAID = "paid"
    UNPAID = "unpaid"
    CANCELED = "canceled"
