from __future__ import annotations

import logging
from typing import Optional

from subscriptions.payment_system.models import SubscribePaymentStatus, PaymentStatus


class AbstractPaymentSystem:

    def __init__(self, product_id: str, product_name: str, subscription_id: str, last_payment: dict,
                 tariff_id: str, tariff_period: str, amount: float,
                 success_url: str, cancel_url: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.last_payment = last_payment
        self.product_id = product_id
        self.product_name = product_name
        self.tariff_id = tariff_id
        self.subscription_id = subscription_id
        self.tariff_period = tariff_period
        self.amount = amount
        self.success_url = success_url
        self.cancel_url = cancel_url

    def process_payment(self):
        """ Запускаем обработку платежа """
        raise NotImplementedError

    def check_payment_status(self) -> Optional[PaymentStatus]:
        """ Проверяем статус платежа """
        raise NotImplementedError

    def check_subscription_status(self) -> Optional[SubscribePaymentStatus]:
        """ Проверяем статус подписки """
        return None

    def refund_payment(self):
        """ Возврат платежа """
        raise NotImplementedError

    def subscription_create(self):
        """ Создание подписки """
        raise NotImplementedError

    def subscription_cancel(self, cancel_at_period_end=True):
        """ Отмена подписки """
        raise NotImplementedError

    def subscription_renew(self):
        """ Продлить подписку"""
        raise NotImplementedError
