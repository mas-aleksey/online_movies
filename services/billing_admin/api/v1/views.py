from django.http import JsonResponse
import logging
import json
from services.notify import send_payment_notify
from subscriptions.models import PaymentHistory
from subscriptions.payment_system.payment_factory import PaymentSystemFactory

LOGGER = logging.getLogger(__file__)


def debug(request):
    print('debug')
    r = send_payment_notify(request.scope['user_id'], '100 руб.', 'Оплата произведена успешно')
    return JsonResponse({'response': r})


def status(request):
    return JsonResponse({'status': 'ok'})


def payment(request, payment_id):
    pay: PaymentHistory = PaymentHistory.objects.filter(pk=payment_id).first()
    ps = PaymentSystemFactory.get_payment_system(pay)
    resp = ps.process_payment()
    LOGGER.error(resp)
    return JsonResponse({'msg': 'create payment'})


def callback(request):
    LOGGER.error('callback execute')
    LOGGER.error(request)
    if request.body:
        data = json.loads(request.body.decode('utf-8'))
        LOGGER.error(data)
    else:
        return JsonResponse({'status': 'ok'})

    return JsonResponse({'status': 'ok'})
