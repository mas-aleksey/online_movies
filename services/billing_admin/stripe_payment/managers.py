from django.db.models import Manager


class StripeIdManager(Manager):
    def products(self):
        from stripe_payment.models import ObjectType
        return self.filter(object_type=ObjectType.PRODUCT)

    def prices(self):
        from stripe_payment.models import ObjectType
        return self.filter(object_type=ObjectType.PRICE)

    def subscriptions(self):
        from stripe_payment.models import ObjectType
        return self.filter(object_type=ObjectType.SUBSCRIPTION)
