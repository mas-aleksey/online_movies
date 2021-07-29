import logging

from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from billing.apps.subscriptions.models import Tariff

logger = logging.getLogger(__file__)


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
