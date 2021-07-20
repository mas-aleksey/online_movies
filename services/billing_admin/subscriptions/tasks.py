from config.celery import app
from django.apps import apps


@app.task(queue="high", timeout=10, default_retry_delay=10, max_retries=30)
def wait_payment_task(payment_id):
    payment_model = apps.get_model('subscriptions', 'PaymentInvoice')
    pay = payment_model.objects.filter(id=payment_id).first()
    pay.payment_system_instance.check_payment_status()