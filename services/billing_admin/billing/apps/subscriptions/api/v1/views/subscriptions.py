import logging

from django.http import JsonResponse, Http404
from django.views import View
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from billing.apps.subscriptions.models import Subscription, AuditEvents
from billing.apps.subscriptions.tasks import unsubscribe_task

logger = logging.getLogger(__file__)


class UserSubscriptionsApi(BaseListView):
    model = Subscription
    paginate_by = 10
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        self.kwargs['user_id'] = request.scope.get('user_id')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.exclude_cancelled().filter_by_user_id(self.kwargs['user_id']).values(
            'id', 'expiration_date', 'status', 'client__user_id',
            'tariff__price', 'tariff__period',
            'discount__name', 'discount__description', 'discount__value',
            'tariff__product__name', 'tariff__product__description', 'tariff__product__access_type'
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        paginator, page, object_list, _ = self.paginate_queryset(self.object_list, self.paginate_by)
        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            'results': list(self.object_list),
        }
        return context

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class UserSubscriptionDetailApi(BaseDetailView):
    model = Subscription
    http_method_names = ['get']

    def dispatch(self, request, *args, **kwargs):
        self.kwargs['user_id'] = request.scope.get('user_id')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        qs = super().get_queryset()
        return qs.filter(
            pk=self.kwargs['subscription_id'],
            client__user_id=self.kwargs['user_id']
        ).first()

    def get_context_data(self, **kwargs):
        if self.object:
            ctx = {
                'id': self.object.id,
                'expiration_date': self.object.expiration_date,
                'status_display': self.object.get_status_display(),
                'status': self.object.status,
                'price': self.object.tariff.price,
                'period': self.object.tariff.period,
                'discount_name': self.object.discount.name if self.object.discount else None,
                'discount_value': self.object.discount.value if self.object.discount else None,
                'tariff_product_name': self.object.tariff.product.name,
                'tariff_product_description': self.object.tariff.product.description
            }
            return ctx
        return {}

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False)


class UserUnsubscribeApi(View):
    """Отписка."""

    http_method_names = ['get']

    def dispatch(self, request, *args, **kwargs):
        self.kwargs['user_id'] = request.scope.get('user_id')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return Subscription.objects.filter(
            pk=self.kwargs['subscription_id'],
            client__user_id=self.kwargs['user_id']
        ).first()

    def get(self, request, *args, **kwargs):
        subscription = self.get_object()
        if not subscription:
            return Http404()

        unsubscribe_task.apply_async((subscription.id,))
        AuditEvents.create(f"user {self.kwargs['user_id']}", 'unsubscribe', subscription)
        return JsonResponse({'status': 'ok'})
