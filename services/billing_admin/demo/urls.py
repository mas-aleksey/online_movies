from django.urls import path

from demo.views import login, profile, movies, subscribe, logout, index

app_name = "demo"

urlpatterns = [
    path('', index, name='login'),
    path('login/', login, name='login'),
    path('profile/', profile, name='profile'),
    path('movies/', movies, name='movies'),
    path('subscribe/', subscribe, name='subscribe'),
    path('logout/', logout, name='logout'),
]
