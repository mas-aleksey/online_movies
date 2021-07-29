import datetime
import json

from django.conf import settings
from yookassa import Configuration, Payment, Refund
from yookassa.domain.response import PaymentResponse, RefundResponse

from billing.apps.subscriptions.payment_system.models import PaymentStatus
from billing.apps.subscriptions.payment_system.payment_system import AbstractPaymentSystem

CONFIG = settings.PAYMENT_SYSTEMS[settings.YOOMONEY]
Configuration.configure(CONFIG["shop_id"], CONFIG["key"])


class YoomoneyPaymentSystem(AbstractPaymentSystem):

    def process_payment(self):
        response = self._create_payment()
        data = {
            'payment_info': json.loads(response.json()),
            'url': response.confirmation.confirmation_url
        }
        return data

    def check_payment_status(self):
        payment_id = self.last_payment['id']
        response: PaymentResponse = Payment.find_one(payment_id=payment_id)
        status = PaymentStatus.CANCELED

        if response.status == 'pending':
            status = PaymentStatus.UNPAID
        elif response.status == 'succeeded':
            status = PaymentStatus.PAID
        elif response.status == 'waiting_for_capture':
            Payment.capture(payment_id)
            status = PaymentStatus.UNPAID

        data = {'payment_info': json.loads(response.json()), 'status': status}
        return data

    def refund_payment(self):
        refund: RefundResponse = Refund.create({
            "amount": {
                "value": self.amount,
                "currency": "RUB"
            },
            "payment_id": self.last_payment['id']
        })
        return refund.status

    def _create_payment(self) -> PaymentResponse:
        return Payment.create(
            {
                "amount": {
                    "value": self.amount,
                    "currency": "RUB"
                },
                "payment_method_data": {
                    "type": "bank_card"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": self.success_url
                },
                "capture": True,
                "save_payment_method": True,
                "description": f"Заказ {self.subscription_id}",
                "metadata": {
                    "created": str(datetime.datetime.now()),
                }
            }
        )

    def subscription_create(self):
        """Создание подписки."""
        return self.process_payment()

    def subscription_cancel(self, cancel_at_period_end=True):
        """Отмена подписки."""
        pass

    def subscription_renew(self):
        """Продлить подписку."""

        payment_method_id = self.last_payment['payment_method']['id']
        response = Payment.create({
            "amount": {
                "value": self.amount,
                "currency": "RUB"
            },
            "payment_method_id": payment_method_id,
            "description": f"Заказ {self.subscription_id}",
        })

        return json.loads(response.json())
