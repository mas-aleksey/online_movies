import abc
from typing import Optional
from .yoomoney import YooMoney


class BillingService(abc.ABC):

    name: str

    def __init__(self, config: dict):
        self._config = config

    @abc.abstractmethod
    def callback(self):
        pass

    @abc.abstractmethod
    def create_payment(self):
        pass


class PaymentFactory:
    def __init__(self, config: dict):
        self._payment_systems = {
            YooMoney.name: YooMoney(config[YooMoney.name])
        }

    def get_billing_system(self, name) -> BillingService:
        return self._payment_systems[name]
