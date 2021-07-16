from django.http import JsonResponse
import logging
import json
from services.notify import send_payment_notify
from subscriptions.models import PaymentHistory

LOGGER = logging.getLogger(__file__)


def debug(request):
    send_payment_notify(request.scope['user_id'], request.scope['email'], '100 руб.', 'Оплата произведена успешно')
    return JsonResponse(request.scope)


def status(request):
    return JsonResponse({'status': 'ok'})


def payment(request, payment_id):
    pay: PaymentHistory = PaymentHistory.objects.filter(pk=payment_id).first()
    ps = pay.payment_system_instance()
    ps.process_payment()


def callback(request):
    LOGGER.error('callback execute')
    LOGGER.error(request)
    if request.body:
        data = json.loads(request.body.decode('utf-8'))
        LOGGER.error(data)
    else:
        return JsonResponse({'status': 'ok'})

    return JsonResponse({'status': 'ok'})
