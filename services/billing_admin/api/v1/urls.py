from django.urls import path

from api.v1.views import debug

urlpatterns = [
    path('debug', debug, name='debug'),
]
