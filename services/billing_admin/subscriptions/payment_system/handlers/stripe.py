import json

import stripe

from subscriptions.payment_system.payment_system import AbstractPaymentSystem
from subscriptions.tasks import wait_payment_task
from django.conf import settings
from subscriptions.models.meta import PaymentStatus

CONFIG = settings.PAYMENT_SYSTEMS[settings.STRIPE]
RETURN_UTL = CONFIG["return_url"]
stripe.api_key = CONFIG["secret_key"]


class StripePaymentSystem(AbstractPaymentSystem):

    def process_payment(self):
        response = stripe.PaymentIntent.create(
            amount=self.payment.amount,
            currency="rub",
            payment_method_types=["card"],
            confirm=True,
            return_url=f'{RETURN_UTL}/{self.payment.subscription.id}?refresh_page=1'
        )

        self.payment.info = json.loads(response.json())
        self.payment.status = PaymentStatus.PENDING
        self.payment.save()
        wait_payment_task.apply_async((self.payment.id,), countdown=5)
        return response['charges']['url']

    def check_payment_status(self):
        payment_id = self.payment.info['id']
        response = stripe.Charge.retrieve(payment_id)

        self.payment.info = json.loads(response.json())
        self.payment.save()

        if response.status == 'pending':
            return False
        elif response.status == 'succeeded':
            self.payment.set_payed_status()
            return True
        else:  # failed
            self.payment.set_cancelled_status()
            return True

    def refund_payment(self):
        refund = stripe.Refund.create(
            charge=self.payment.info['id']
        )
        return refund["status"]
