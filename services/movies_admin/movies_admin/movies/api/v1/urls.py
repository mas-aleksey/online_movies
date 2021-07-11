from django.urls import path

from .views import MoviesListApi, MoviesDetailApi

urlpatterns = [
    path('movies/', MoviesListApi.as_view()),
    path('movies/<uuid:pk>', MoviesDetailApi.as_view()),
]
