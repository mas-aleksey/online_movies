from django.urls import path

from demo.views import login, profile, movies, tariffs, logout, index, movies_detail, tariff

app_name = "demo"

urlpatterns = [
    path('', index, name='login'),
    path('login/', login, name='login'),
    path('profile/', profile, name='profile'),
    path('movies/', movies, name='movies'),
    path('movies/<str:movies_id>', movies_detail, name='movies_detail'),
    path('tariffs/', tariffs, name='tariffs'),
    path('tariffs/<str:tariff_id>', tariff, name='tariff'),
    path('logout/', logout, name='logout'),
]
