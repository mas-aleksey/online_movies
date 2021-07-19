from django.http import JsonResponse, HttpResponseRedirect
import logging
import json
from subscriptions.models import PaymentInvoice
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from subscriptions.models import Tariff, Subscription
from subscriptions.payment_system.payment_factory import PaymentSystemFactory


LOGGER = logging.getLogger(__file__)


def status(request):
    return JsonResponse({'status': 'ok'})


def create_subscription(data, scope):
    LOGGER.error(data)
    LOGGER.error(scope)
    return {
        **data, **scope
    }


def make_order(request):
    """
    {
        'tariff_id',
        'payment_system'
    }
    :param request:
    :param tariff_id:
    :return:
    """
    LOGGER.error(request.method)
    if request.method == 'POST':
        data = (json.loads(request.body))
        ctx = create_subscription(data, request.scope)
        return JsonResponse(ctx)

    # redirect to payment_system
    return JsonResponse({'status': 'ok'})


def payment(request, payment_id):
    pay: PaymentInvoice = PaymentInvoice.objects.filter(pk=payment_id).first()
    ps = PaymentSystemFactory.get_payment_system(pay)
    resp = ps.process_payment()
    return HttpResponseRedirect(resp.confirmation.confirmation_url)


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
            'id', 'price', 'period',
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

    def get(self, request, *args, **kwargs):
        self.kwargs['user_id'] = request.scope.get('user_id')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.values(
            'expiration_date', 'status', 'client__id',
            'tariff__price', 'tariff__period',
            'discount__name', 'discount__description', 'discount__value',
            'tariff__product__name', 'tariff__product__description', 'tariff__product__access_type'
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        paginator, page, object_list, _ = self.paginate_queryset(self.object_list, self.paginate_by)
        if self.kwargs['user_id']:
            object_list = [
                subscr for subscr in self.object_list
                if subscr['client__id'] == self.kwargs['user_id']
            ]
        else:
            # TODO: object_list = []
            object_list = self.object_list
        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            'results': list(object_list),
        }
        return context

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)
