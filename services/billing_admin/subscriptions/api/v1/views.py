import json
import logging

from django.contrib.postgres.aggregates import ArrayAgg
from django.http import JsonResponse, Http404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

import subscriptions.utils as utils
from subscriptions.models.models import Tariff, Subscription, Product, AuditEvents
from subscriptions.tasks import unsubscribe_task

LOGGER = logging.getLogger(__file__)


def status(request):
    return JsonResponse({'status': 'ok'})


def create_new_subscription(data, scope):
    user_id = scope['user_id']
    user_email = scope['email']
    payment_system = data['payment_system']
    tariff_id = data['tariff_id']

    subscription = utils.create_subscription(user_id, tariff_id, payment_system, user_email)
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
        try:
            url = create_new_subscription(data, request.scope)
        except Exception as e:
            LOGGER.error(e)
            return JsonResponse({'status': 'failed', 'msg': str(e)}, status=500)
        return JsonResponse({'confirmation_url': url})

    # redirect to payment_system
    return JsonResponse({'status': 'ok'})


def callback(request):
    LOGGER.error('callback execute')
    LOGGER.error(request)
    if request.body:
        data = json.loads(request.body.decode('utf-8'))
        LOGGER.error(data)
    else:
        return JsonResponse({'status': 'ok'})

    return JsonResponse({'status': 'ok'})


class BaseTariffApiMixin:
    model = Tariff
    http_method_names = ['get']

    def get_queryset(self):
        return self.model.objects.values(
            'id', 'price', 'period', 'product__id',
            'discount__name', 'discount__description', 'discount__value',
            'product__name', 'product__description', 'product__access_type'
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class TariffDetailApi(BaseTariffApiMixin, BaseDetailView):

    def get_object(self, queryset=None):
        qs = super().get_queryset()
        return qs.filter(pk=self.kwargs['tariff_id']).first()

    def get_context_data(self, **kwargs):
        return kwargs['object']


class TariffListApi(BaseTariffApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        paginator, page, object_list, _ = self.paginate_queryset(self.object_list, self.paginate_by)
        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            'results': list(object_list),
        }
        return context


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


class ProductListApi(BaseListView):
    model = Product
    paginate_by = 50
    http_method_names = ['get']

    def get_queryset(self):
        return self.model.objects.values(
            'id', 'name', 'description', 'access_type'
        ).annotate(
            tariff_ids=ArrayAgg(
                'tariffs__id',
            ),
            tariff_periods=ArrayAgg(
                'tariffs__period',
            ),
            tariff_prices=ArrayAgg(
                'tariffs__price',
            ),
            discounts=ArrayAgg(
                'tariffs__discount__value',
            ),
        ).order_by('id')

    @staticmethod
    def prepare_item(product: dict) -> dict:
        item = {
            'id': product['id'],
            'name': product['name'],
            'description': product['description'],
            'access_type': product['access_type'],
            'tariffs': []
        }
        for _id, period, price, discount in zip(
                product['tariff_ids'], product['tariff_periods'],
                product['tariff_prices'], product['discounts']
        ):
            tariff = {'id': _id, 'period': period, 'price': price, 'discount': discount}
            item['tariffs'].append(tariff)
        return item

    def get_context_data(self, *, object_list=None, **kwargs):
        paginator, page, object_list, _ = self.paginate_queryset(self.object_list, self.paginate_by)
        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            'results': [self.prepare_item(item) for item in self.object_list],
        }
        return context

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class UserUnsubscribeApi(View):
    """Отписка"""

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
        return JsonResponse({'status': 'ok'})
