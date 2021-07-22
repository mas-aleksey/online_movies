import json

from subscriptions.payment_system.payment_system import AbstractPaymentSystem
from subscriptions.tasks import wait_payment_task
from django.conf import settings
from yookassa import Configuration, Payment, Refund
from yookassa.domain.response import PaymentResponse, RefundResponse
from subscriptions.models.meta import PaymentStatus

CONFIG = settings.PAYMENT_SYSTEMS[settings.YOOMONEY]
RETURN_UTL = CONFIG["return_url"]

Configuration.configure(CONFIG["shop_id"], CONFIG["key"])


class YoomoneyPaymentSystem(AbstractPaymentSystem):

    def process_payment(self):
        response = self._create_payment()
        self.payment.info = json.loads(response.json())
        self.payment.status = PaymentStatus.PENDING
        self.payment.save()
        wait_payment_task.apply_async((self.payment.id,), countdown=5)
        return response.confirmation.confirmation_url

    def check_payment_status(self):
        payment_id = self.payment.info['id']
        response: PaymentResponse = Payment.find_one(payment_id=payment_id)

        self.payment.info = json.loads(response.json())
        self.payment.save()

        if response.status == 'pending':
            return False
        elif response.status == 'succeeded':
            self.payment.set_payed_status()
            self.payment.subscription.set_active()
            return True
        elif response.status == 'waiting_for_capture':
            Payment.capture(self.payment.info['id'])
            return False
        else:  # canceled
            self.payment.set_cancelled_status()
            return True

    def refund_payment(self):
        refund: RefundResponse = Refund.create({
            "amount": {
                "value": self.payment.amount,
                "currency": "RUB"
            },
            "payment_id": self.payment.info['id']
        })
        return refund.status

    def _create_payment(self) -> PaymentResponse:
        return Payment.create(
            {
                "amount": {
                    "value": self.payment.amount,
                    "currency": "RUB"
                },
                "payment_method_data": {
                    "type": "bank_card"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": f'{RETURN_UTL}/{self.payment.subscription.id}?refresh_page=1'
                },
                "capture": True,
                "save_payment_method": True,
                "description": f"Заказ {self.payment.id}",
                "metadata": {
                    "created": str(self.payment.created),
                }
            }
        )

    def subscription_cancel(self, cancel_at_period_end=True):
        """ Отмена подписки """
        pass

    def subscription_renew(self):
        """ Продлить подписку"""
        pass
