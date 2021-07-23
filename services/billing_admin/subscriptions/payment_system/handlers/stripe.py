from typing import Optional

from stripe_payment.models import SubscriptionInfoDataclass
from stripe_payment.services.payment import create_subscription_checkout, get_subscription_info, subscription_cancel, \
    subscription_refund
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

    def check_payment_status(self) -> Optional[PaymentStatus]:
        payment_id = self.last_payment['id']
        data = checkout_retrieve_stripe(payment_id)

        stripe_subscription_id = data.get('subscription')
        if stripe_subscription_id:
            create_or_update_subscription_id(
                billing_subscription_id=str(self.subscription_id),
                stripe_subscription_id=stripe_subscription_id
            )

        status = data['payment_status']
        if status == 'paid':
            return PaymentStatus.PAYED
        elif status == 'unpaid':
            return PaymentStatus.UNPAID
        return PaymentStatus.CANCELED

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
        pass

    def subscription_cancel(self, cancel_at_period_end=True):
        """ Отмена подписки """
        data = subscription_cancel(self.subscription_id, cancel_at_period_end)
        return data
