import logging

from drf_yasg import openapi
from drf_yasg.openapi import Schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.apps.subscriptions.api.v1.serializers import PaymentSerializer
from billing.apps.subscriptions.services.subscription import subscription_create

logger = logging.getLogger(__file__)


class PaymentAPIView(APIView):
    """Представление для запуска оплаты подписки."""
    http_method_names = ['post', ]

    @swagger_auto_schema(
        request_body=PaymentSerializer,
        responses={
            200: openapi.Response(
                'Success', Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'confirmation_url':
                            Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response('Bad request')
        }
    )
    def post(self, request):
        serializer = PaymentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user_id = request.scope['user_id']
        payment_system = data['payment_system']
        tariff_id = data['tariff_id']
        subscription = subscription_create(user_id, tariff_id, payment_system)
        url = subscription.process_confirm()
        return Response({'confirmation_url': url})
