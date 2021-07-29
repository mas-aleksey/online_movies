import logging

from django.contrib.postgres.aggregates import ArrayAgg
from django.http import JsonResponse
from django.views.generic.list import BaseListView

from billing.apps.subscriptions.models import Product

logger = logging.getLogger(__file__)


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
