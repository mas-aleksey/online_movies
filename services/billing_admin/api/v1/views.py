from django.http import JsonResponse
import logging
from services.notify import send_payment_notify

LOGGER = logging.getLogger(__file__)


def debug(request):
    print('debug')
    r = send_payment_notify(request.scope['user_id'], '100 руб.', 'Оплата произведена успешно')
    return JsonResponse({'response': r})


