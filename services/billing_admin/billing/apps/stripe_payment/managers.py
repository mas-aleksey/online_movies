from django.db.models import Manager
from billing.apps.stripe_payment import models


class StripeIdManager(Manager):
    def products(self):
        return self.filter(object_type=models.ObjectType.PRODUCT)

    def prices(self):
        return self.filter(object_type=models.ObjectType.PRICE)

    def subscriptions(self):
        return self.filter(object_type=models.ObjectType.SUBSCRIPTION)
