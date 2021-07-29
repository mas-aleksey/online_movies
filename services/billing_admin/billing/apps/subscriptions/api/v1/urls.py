from django.urls import path

from .views import (
    TariffDetailApi, UserSubscriptionsApi, ProductListApi,
    PaymentAPIView, UserSubscriptionDetailApi, UserUnsubscribeApi
)

urlpatterns = [
    path('products/', ProductListApi.as_view()),
    path('tariff/<uuid:tariff_id>', TariffDetailApi.as_view()),
    path('order/', PaymentAPIView.as_view()),
    path('subscriptions/', UserSubscriptionsApi.as_view()),
    path('subscriptions/<uuid:subscription_id>', UserSubscriptionDetailApi.as_view()),
    path('subscriptions/<uuid:subscription_id>/unsubscribe', UserUnsubscribeApi.as_view()),
]
