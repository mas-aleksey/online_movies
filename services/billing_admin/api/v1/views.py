from django.http import JsonResponse

from services.notify import send_payment_notify


def debug(request):
    send_payment_notify(request.scope['user_id'], request.scope['email'], '100 руб.', 'Оплата произведена успешно')
    return JsonResponse(request.scope)
