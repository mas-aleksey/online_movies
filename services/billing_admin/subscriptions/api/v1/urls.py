from django.urls import path

from .views import (
    TariffListApi, TariffDetailApi, UserSubscriptionsApi,
    make_order, status, payment, callback
)


urlpatterns = [
    path('tariffs/', TariffListApi.as_view()),
    path('tariff/<uuid:tariff_id>', TariffDetailApi.as_view()),
    path('order/<uuid:tariff_id>', make_order, name="make_order"),
    path('subscriptions/', UserSubscriptionsApi.as_view()),
    path('status/', status, name='status'),
    path('payment/<uuid:payment_id>', payment, name='payment'),
    path('callback/', callback, name='callback'),
]
