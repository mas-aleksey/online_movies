from config.celery import app
from django.apps import apps


@app.task(queue="high", timeout=60*5, default_retry_delay=10, max_retries=30)
def wait_payment_task(payment_id):
    payment_model = apps.get_model('subscriptions', 'PaymentInvoice')
    pay = payment_model.objects.filter(id=payment_id).first()
    is_finish = pay.payment_system_instance.check_payment_status()
    print(f'wait_payment_task payed: {is_finish}')
    if is_finish:
        print('payment finished')
        return
    else:
        print('retry check payment status')
        wait_payment_task.apply_async((payment_id,), countdown=5)
