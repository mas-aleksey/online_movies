# Generated by Django 3.1 on 2021-07-24 18:09

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0006_subscription_payment_system'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditEvents',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('who', models.CharField(max_length=50, verbose_name='Инициатор события')),
                ('what', models.CharField(max_length=50, verbose_name='Событие')),
                ('related_name', models.CharField(max_length=50, verbose_name='Объект')),
                ('related_id', models.CharField(max_length=50, verbose_name='Id объекта')),
                ('details', models.TextField(blank=True, null=True, verbose_name='Подробности')),
            ],
            options={
                'verbose_name': 'событие',
                'verbose_name_plural': 'событий',
            },
        ),
    ]
