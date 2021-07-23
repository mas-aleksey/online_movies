import datetime
import json
from typing import Optional

from django.conf import settings
from yookassa import Configuration, Payment, Refund
from yookassa.domain.response import PaymentResponse, RefundResponse

from subscriptions.payment_system.models import PaymentStatus
from subscriptions.payment_system.payment_system import AbstractPaymentSystem

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

    def check_payment_status(self) -> Optional[PaymentStatus]:
        payment_id = self.last_payment['id']
        response: PaymentResponse = Payment.find_one(payment_id=payment_id)

        if response.status == 'pending':
            return PaymentStatus.UNPAID
        elif response.status == 'succeeded':
            return PaymentStatus.PAID
        elif response.status == 'waiting_for_capture':
            Payment.capture(payment_id)
            return PaymentStatus.UNPAID

        return PaymentStatus.CANCELED

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
        """ Создание подписки """
        return self.process_payment()

    def subscription_cancel(self, cancel_at_period_end=True):
        """ Отмена подписки """
        pass

    def subscription_renew(self):
        """ Продлить подписку"""
        pass
