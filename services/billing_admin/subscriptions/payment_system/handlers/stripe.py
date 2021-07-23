from typing import Optional

from stripe_payment.models import SubscriptionInfoDataclass
from stripe_payment.services.payment import create_subscription_checkout, get_subscription_info, subscription_cancel, \
    subscription_refund, get_latest_invoice
from stripe_payment.services.stripe_api import checkout_retrieve_stripe
from stripe_payment.services.subscription import create_or_update_subscription_id
from subscriptions.models.meta import SubscriptionPeriods
from subscriptions.payment_system.models import SubscribePaymentStatus, PaymentStatus
from subscriptions.payment_system.payment_system import AbstractPaymentSystem

PERIODS = {
    str(SubscriptionPeriods.MONTHLY): "month",
    str(SubscriptionPeriods.YEARLY): "year"
}


class StripePaymentSystem(AbstractPaymentSystem):

    def process_payment(self):
        pass

    def check_subscription_status(self) -> Optional[SubscribePaymentStatus]:
        data = get_subscription_info(self.subscription_id)
        status = data['status']
        if status == 'active':
            return SubscribePaymentStatus.ACTIVE
        return SubscribePaymentStatus.CANCELLED

    def check_payment_status(self):
        payment_id = self.last_payment['id']
        data = self.last_payment

        stripe_subscription_id = self.last_payment.get('subscription')
        if not stripe_subscription_id:
            data = checkout_retrieve_stripe(payment_id)
            stripe_subscription_id = data.get('subscription')

        if stripe_subscription_id:
            create_or_update_subscription_id(
                billing_subscription_id=str(self.subscription_id),
                stripe_subscription_id=stripe_subscription_id
            )
            data = get_latest_invoice(self.subscription_id)

        status = data['status'] if data['object'] == 'invoice' else data['payment_status']

        data = {'payment_info': data, 'status': PaymentStatus.CANCELED}
        if status == 'paid':
            data['status'] = PaymentStatus.PAID
        elif status == 'unpaid':
            data['status'] = PaymentStatus.UNPAID

        return data

    def refund_payment(self):
        """возврат платежа"""
        subscription_id = str(self.subscription_id)
        data = subscription_refund(subscription_id)
        return data

    def subscription_create(self):
        """ Создание подписки """

        amount = int(self.amount * 100)
        period = PERIODS[self.tariff_period]

        subscription = SubscriptionInfoDataclass(
            product_id=self.product_id,
            product_name=self.product_name,
            tariff_id=self.tariff_id,
            tariff_period=period,
            amount=amount,
            success_url=self.success_url,
            cancel_url=self.cancel_url
        )
        response = create_subscription_checkout(subscription)
        data = {
            'payment_info': response,
            'url': response['url']
        }
        return data

    def subscription_renew(self):
        """ Продлить подписку"""
        data = get_latest_invoice(self.subscription_id)

        payment_id = self.last_payment['id']
        if data['id'] == payment_id:  # уже сохранили этот платеж
            return None

        return data

    def subscription_cancel(self, cancel_at_period_end=True):
        """ Отмена подписки """
        data = subscription_cancel(self.subscription_id, cancel_at_period_end)
        return data
