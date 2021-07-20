import os
from celery import Celery
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

app = Celery('admin_app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(queue="low", timeout=60 * 10)
def debug_task():
    print('celery debug task!')


@app.task(queue="high", timeout=10, default_retry_delay=10, max_retries=30)
def wait_payment_task(payment_id):
    payment_model = apps.get_model('subscriptions', 'PaymentInvoice')
    pay = payment_model.objects.filter(id=payment_id).first()
    pay.payment_system_instance.check_payment_status()
