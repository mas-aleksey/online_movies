import logging

from rest_framework import generics

from billing.apps.subscriptions.api.v1.serializers import ProductSerializer
from billing.apps.subscriptions.models import Product

logger = logging.getLogger(__file__)


class ProductListApi(generics.ListAPIView):
    http_method_names = ['get', ]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
