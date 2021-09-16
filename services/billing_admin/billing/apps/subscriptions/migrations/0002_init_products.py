from uuid import uuid4
from django.db import migrations


def init_products(apps, schema_editor):
    Product = apps.get_model('subscriptions', 'Product')
    Discount = apps.get_model('subscriptions', 'Discount')
    Tariff = apps.get_model('subscriptions', 'Tariff')

    discount = Discount(id=uuid4(), name='Скидка новым подписчикам', code='NEW', value=10)
    discount.save()

    standard = Product(
        id=uuid4(), name='Стандартная подписка', description='Смотрите фильмы по подписке!', access_type='standard'
    )
    standard.save()

    extra = Product(
        id=uuid4(), name='Расширенная подписка', description='Смотрите фильмы по подписке!', access_type='extra'
    )
    extra.save()

    Tariff(id=uuid4(), product=standard, price=100, period='per month').save()
    Tariff(id=uuid4(), product=standard, price=1000, period='per year').save()

    Tariff(id=uuid4(), product=extra, price=500, period='per month', discount=discount).save()
    Tariff(id=uuid4(), product=extra, price=5000, period='per year', discount=discount).save()


class Migration(migrations.Migration):
    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(init_products)
    ]
