# Generated by Django 3.1 on 2021-07-15 12:41

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('user_id', models.UUIDField(unique=True, verbose_name='uuid пользователя')),
            ],
            options={
                'verbose_name': 'клиент',
                'verbose_name_plural': 'клиенты',
            },
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='название')),
                ('code', models.CharField(blank=True, max_length=50, null=True, verbose_name='промокод')),
                ('description', models.TextField(blank=True, null=True, verbose_name='описание')),
                ('value', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='размер скидки')),
                ('is_active', models.BooleanField(default=True, verbose_name='активная скидка')),
            ],
            options={
                'verbose_name': 'скидка',
                'verbose_name_plural': 'скидки',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='название')),
                ('description', models.TextField(blank=True, null=True, verbose_name='описание')),
                ('access_type', models.CharField(choices=[('free', 'бесплатный доступ'), ('standard', 'обычная подписка'), ('extra', 'расширенная подписка')], default='free', max_length=64, verbose_name='Тип доступа к фильмам')),
            ],
            options={
                'verbose_name': 'продукт',
                'verbose_name_plural': 'продукты',
            },
        ),
        migrations.CreateModel(
            name='Tariff',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('price', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='цена')),
                ('period', models.CharField(choices=[('per month', 'каждый месяц'), ('per year', 'каждый год')], default='per month', max_length=64, verbose_name='Период списания')),
                ('discount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='subscriptions.discount', verbose_name='скидка')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subscriptions.product', verbose_name='продукт')),
            ],
            options={
                'verbose_name': 'тариф',
                'verbose_name_plural': 'тарифы',
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('expiration_date', models.DateField(verbose_name='дата окончания')),
                ('status', models.CharField(choices=[('inactive', 'Не активная'), ('active', 'Активная'), ('expired', 'Истек срок действия'), ('cancelled', 'Подписка отмененна')], default='inactive', max_length=64, verbose_name='Статус подписки')),
                ('payment_system', models.CharField(choices=[('dummy', 'Псевдо платежная система'), ('yoomoney', 'Юмани платежная система')], default='yoomoney', max_length=64, verbose_name='Тип платежной системы')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subscriptions.client', verbose_name='клиент')),
                ('discount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='subscriptions.discount', verbose_name='скидка')),
                ('tariff', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='subscriptions.tariff', verbose_name='тариф')),
            ],
            options={
                'verbose_name': 'подписка',
                'verbose_name_plural': 'подписки',
            },
        ),
        migrations.CreateModel(
            name='PaymentHistory',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('amount', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='конечная цена')),
                ('payment_info', models.TextField(blank=True, null=True, verbose_name='информация о платеже')),
                ('status', models.CharField(choices=[('not_payed', 'Не оплачен'), ('payed', 'Оплачен'), ('pending', 'Ждем подтверждения оплаты'), ('failed', 'Оплата не успешна'), ('cancelled', 'Оплата отмененна')], default='not_payed', max_length=64, verbose_name='Статус платежа')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subscriptions.subscription', verbose_name='подписка')),
            ],
            options={
                'verbose_name': 'платеж',
                'verbose_name_plural': 'платежи',
            },
        )
    ]