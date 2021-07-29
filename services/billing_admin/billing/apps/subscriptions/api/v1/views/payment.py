import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from billing.apps.subscriptions.services.subscription import subscription_create

logger = logging.getLogger(__file__)


def create_new_subscription(data, scope):
    user_id = scope['user_id']
    payment_system = data['payment_system']
    tariff_id = data['tariff_id']

    subscription = subscription_create(user_id, tariff_id, payment_system)
    url = subscription.process_confirm()
    return url


@csrf_exempt
def make_order(request):
    """
    {
        'tariff_id',
        'payment_system'
    }
    :param request:
    :return:
    """
    if request.method == 'POST':
        data = (json.loads(request.body))
        url = create_new_subscription(data, request.scope)
        try:
            pass
        except Exception as e:
            logger.error(e)
            return JsonResponse({'status': 'failed', 'msg': str(e)}, status=500)
        return JsonResponse({'confirmation_url': url})

    # redirect to payment_system
    return JsonResponse({'status': 'ok'})
