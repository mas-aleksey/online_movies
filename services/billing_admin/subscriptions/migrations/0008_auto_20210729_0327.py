# Generated by Django 3.1 on 2021-07-29 03:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0007_auditevents'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='auditevents',
            options={'verbose_name': 'событие', 'verbose_name_plural': 'события'},
        ),
    ]
