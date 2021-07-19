from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from requests import HTTPError

from demo.forms import LoginForm
from demo.services import auth_profile, auth_logout


def index(request):
    access_token = request.session.get('access_token', '')
    if not access_token:
        return HttpResponseRedirect(reverse('demo:login'))
    return HttpResponseRedirect(reverse('demo:profile'))


def login(request):
    """логин"""

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            request.session['access_token'] = form.access_token
            request.session['refresh_token'] = form.refresh_token
            return HttpResponseRedirect(reverse('demo:profile'))
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def profile(request):
    """профиль пользователя"""

    if not request.session.get('refresh_token'):
        return HttpResponseRedirect(reverse('demo:login'))

    ctx = {
        'access_token': None,
        'refresh_token': None
    }
    try:
        ctx = auth_profile(request.session['refresh_token'])
    except HTTPError as e:
        ctx['errors'] = str(e)

    request.session['access_token'] = ctx['access_token']
    request.session['refresh_token'] = ctx['refresh_token']

    return render(request, 'profile.html', ctx)


def logout(request):
    """профиль пользователя"""

    access_token = request.session.get('access_token', '')

    if access_token:
        request.session['access_token'] = None
        request.session['refresh_token'] = None

    auth_logout(access_token)

    return HttpResponseRedirect(reverse('demo:login'))


def movies(request):
    """доступные фильмы"""
    access_token = request.session.get('access_token')
    if not access_token:
        return HttpResponseRedirect(reverse('demo:login'))
    ctx = {
        'autocomplete_url': f'{settings.ASYNC_SERVER}/api/v1/film/search?limit=50&page=1',
        'access_token': access_token
    }
    return render(request, 'movies.html', ctx)


def subscribe(request):
    """Оформить подписку"""
    access_token = request.session.get('access_token')
    if not access_token:
        return HttpResponseRedirect(reverse('demo:login'))
    return render(request, 'subscribe.html')
