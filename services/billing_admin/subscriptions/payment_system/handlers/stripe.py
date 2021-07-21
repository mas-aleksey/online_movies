from django.conf import settings

from stripe_payment.models import SubscriptionInfoDataclass
from stripe_payment.services.payment import create_subscription_checkout, get_subscription_info
from stripe_payment.services.stripe_api import checkout_retrieve_stripe
from stripe_payment.services.subscription import create_or_update_subscription_id
from subscriptions.models.meta import PaymentStatus, SubscriptionPeriods
from subscriptions.payment_system.payment_system import AbstractPaymentSystem
from subscriptions.tasks import wait_payment_task

CONFIG = settings.PAYMENT_SYSTEMS[settings.STRIPE]
RETURN_UTL = CONFIG["return_url"]

PERIODS = {
    SubscriptionPeriods.MONTHLY: "month",
    SubscriptionPeriods.YEARLY: "year"
}


class StripePaymentSystem(AbstractPaymentSystem):

    def process_payment(self):
        amount = int(self.payment.amount * 100)

        tariff = self.payment.subscription.tariff
        period = PERIODS[tariff.period]
        return_url = f'{RETURN_UTL}/{self.payment.subscription.id}?refresh_page=1'

        subscription = SubscriptionInfoDataclass(
            product_id=str(tariff.product.id),
            product_name=tariff.product.name,
            tariff_id=str(tariff.id),
            tariff_period=period,
            amount=amount,
            success_url=return_url,
            cancel_url=return_url
        )

        response = create_subscription_checkout(subscription)

        self.payment.info = response
        self.payment.status = PaymentStatus.PENDING
        self.payment.save()
        self.check_payment_status()
        wait_payment_task.apply_async((self.payment.id,), countdown=5)
        return response['url']

    def check_subscribe_status(self):
        data = get_subscription_info(str(self.payment.subscription.id))
        status = data['status']

        if status == 'active':
            self.payment.subscription.set_active()
            return True
        else:  # failed
            self.payment.set_cancelled_status()
            return False

    def check_payment_status(self):
        payment_id = self.payment.info['id']
        data = checkout_retrieve_stripe(payment_id)

        stripe_subscription_id = data.get('subscription')
        if stripe_subscription_id:
            create_or_update_subscription_id(
                billing_subscription_id=str(self.payment.subscription.id),
                stripe_subscription_id=stripe_subscription_id
            )
            return self.check_subscribe_status()

        self.payment.info = data
        self.payment.save()
        status = data['payment_status']

        if status == 'unpaid':
            return False
        elif status == 'paid':
            self.payment.set_payed_status()
            return True
        else:  # failed
            self.payment.set_cancelled_status()
            return False

    def refund_payment(self):
        # TODO refund
        pass
