import logging
from subscriptions.models import PaymentInvoice


class AbstractPaymentSystem:

    def __init__(self, payment: PaymentInvoice):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.payment = payment

    def process_payment(self):
        """ Запускаем обработку платежа """
        raise NotImplementedError

    def callback(self, *args, **kwargs):
        """ обработка callback метода """
        raise NotImplementedError
