from subscriptions.payment_system.payment_factory import AbstractPaymentSystem


class DummyPaymentSystem(AbstractPaymentSystem):

    def process_payment(self):
        pass

    def callback(self):
        pass