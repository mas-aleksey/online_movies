from django.urls import path

from .views import (
    TariffListApi, TariffDetailApi, UserSubscriptionsApi,
    make_order, status, callback, UserSubscriptionDetailApi
)


urlpatterns = [
    path('tariffs/', TariffListApi.as_view()),
    path('tariff/<uuid:tariff_id>', TariffDetailApi.as_view()),
    path('order/', make_order, name="make_order"),
    path('subscriptions/', UserSubscriptionsApi.as_view()),
    path('subscriptions/<uuid:subscription_id>', UserSubscriptionDetailApi.as_view()),
    path('status/', status, name='status'),
    path('callback/', callback, name='callback'),
]
