from django.urls import path, include

urlpatterns = [
    path('v1/', include('billing.apps.subscriptions.api.v1.urls')),
]
