from django.http import JsonResponse

from services.notify import send_payment_notify


def debug(request):
    print('debug')
    send_payment_notify(request.scope['user_id'], '100 руб.', 'Оплата произведена успешно')
    return JsonResponse(request.scope)
