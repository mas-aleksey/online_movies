from django.urls import path

from demo.views import login, profile, movies, logout, index, movies_detail, tariff, order, subscribe, \
    subscriptions, products,unsubscribe

app_name = "demo"

urlpatterns = [
    path('', index, name='login'),
    path('login/', login, name='login'),
    path('profile/', profile, name='profile'),
    path('movies/', movies, name='movies'),
    path('movies/<str:movies_id>', movies_detail, name='movies_detail'),
    path('products/', products, name='products'),
    path('tariff/<str:tariff_id>', tariff, name='tariff'),
    path('order/', order, name='order'),
    path('subscriptions/', subscriptions, name='subscriptions'),
    path('subscriptions/<str:subscribe_id>', subscribe, name='subscribe'),
    path('subscriptions/<str:subscribe_id>/unsubscribe', unsubscribe, name='unsubscribe'),
    path('logout/', logout, name='logout'),
]
