from django.urls import path

from api.v1.views import debug, callback, payment, status

urlpatterns = [
    path('debug', debug, name='debug'),
    path('status/', status, name='status'),
    path('payment/<uuid:payment_id>', payment, name='payment'),
    path('callback/', callback, name='callback'),
]
