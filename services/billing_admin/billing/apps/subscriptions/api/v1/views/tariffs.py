import logging

from rest_framework import generics

from billing.apps.subscriptions.api.v1.serializers import TariffDetailSerializer
from billing.apps.subscriptions.models import Tariff

logger = logging.getLogger(__file__)


class TariffDetailApi(generics.RetrieveAPIView):
    lookup_url_kwarg = 'tariff_id'
    http_method_names = ['get', ]
    queryset = Tariff.objects.all()
    serializer_class = TariffDetailSerializer
