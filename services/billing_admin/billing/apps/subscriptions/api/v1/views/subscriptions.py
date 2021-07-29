import logging

from django.http import Http404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.apps.subscriptions.api.v1.serializers import SubscriptionSerializer
from billing.apps.subscriptions.models import Subscription, AuditEvents
from billing.apps.subscriptions.tasks import unsubscribe_task

logger = logging.getLogger(__file__)


class FilterByUserMixin:
    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.scope.get('user_id')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = self.queryset
        qs = qs.filter_by_user_id(self.user_id)
        return qs


class UserSubscriptionsApi(FilterByUserMixin, generics.ListAPIView):
    """Список подписок пользователя."""
    http_method_names = ['get', ]
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.exclude_cancelled()
        return qs


class UserSubscriptionDetailApi(FilterByUserMixin, generics.RetrieveAPIView):
    """Детальная информация о подписке."""
    http_method_names = ['get', ]
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_object(self):
        qs = super().get_queryset()
        return qs.filter(pk=self.kwargs['subscription_id']).first()


class UserUnsubscribeApi(FilterByUserMixin, APIView):
    """Отписка."""

    http_method_names = ['get']
    queryset = Subscription.objects.all()

    def get_object(self):
        qs = super().get_queryset()
        return qs.filter(pk=self.kwargs['subscription_id']).first()

    def get(self, request, *args, **kwargs):
        subscription = self.get_object()
        if not subscription:
            return Http404()

        unsubscribe_task.apply_async((subscription.id,))
        AuditEvents.create(f"user {self.user_id}", 'unsubscribe', subscription)
        return Response({'status': 'ok'})
