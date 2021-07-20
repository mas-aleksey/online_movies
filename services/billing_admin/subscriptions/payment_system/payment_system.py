from __future__ import annotations
from typing import TYPE_CHECKING
import logging
if TYPE_CHECKING:
    from subscriptions.models.models import PaymentInvoice


class AbstractPaymentSystem:

    def __init__(self, payment: PaymentInvoice):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.payment = payment

    def process_payment(self):
        """ Запускаем обработку платежа """
        raise NotImplementedError

    def check_payment_status(self):
        """ Проверяем статус платежа """
        raise NotImplementedError

    def refund_payment(self):
        """ Возврат платежа """
        raise NotImplementedError
