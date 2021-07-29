import uuid
from django.test import TestCase
from subscriptions.models.models import Tariff, Product
from subscriptions.utils import get_or_create_client, create_subscription


class UsersManagersTests(TestCase):
    def test_create_user(self):

        client = get_or_create_client('fb167b09-7d56-4330-814a-0ba799e985de')
        self.assertEqual(client.user_id, 'fb167b09-7d56-4330-814a-0ba799e985de')
        tariff_id = uuid.uuid4()
        prod = Product.objects.first()
        self.assertIsNotNone(prod)
        t = Tariff(id=tariff_id, product=prod, price=10, discount=None)
        t.save()
        s = create_subscription('fb167b09-7d56-4330-814a-0ba799e985de', tariff_id)
