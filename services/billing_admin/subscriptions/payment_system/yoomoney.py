from subscriptions.payment_system.payment_factory import BillingService


class YooMoney(BillingService):

    name = 'YooMoney'

    def create_payment(self):
        pass

    def callback(self):
        pass
