from django.urls import path, include

urlpatterns = [
    path('v1/', include('subscriptions.api.v1.urls')),
]