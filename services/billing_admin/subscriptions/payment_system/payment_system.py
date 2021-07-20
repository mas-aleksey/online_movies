import logging
from django.apps import apps

PaymentInvoice = apps.get_model('subscriptions', 'PaymentInvoice')


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

    def callback(self, *args, **kwargs):
        """ обработка callback метода """
        raise NotImplementedError
