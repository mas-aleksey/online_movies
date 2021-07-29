from django.urls import path

from .views import (
    TariffListApi, TariffDetailApi, UserSubscriptionsApi, ProductListApi,
    make_order, UserSubscriptionDetailApi, UserUnsubscribeApi
)

urlpatterns = [
    path('tariffs/', TariffListApi.as_view()),
    path('products/', ProductListApi.as_view()),
    path('tariff/<uuid:tariff_id>', TariffDetailApi.as_view()),
    path('order/', make_order, name="make_order"),
    path('subscriptions/', UserSubscriptionsApi.as_view()),
    path('subscriptions/<uuid:subscription_id>', UserSubscriptionDetailApi.as_view()),
    path('subscriptions/<uuid:subscription_id>/unsubscribe', UserUnsubscribeApi.as_view()),
]
