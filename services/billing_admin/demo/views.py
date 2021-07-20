from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from demo.forms import LoginForm
from demo.services import auth_profile, auth_logout, async_movies_search, async_movies_detail, billing_tariffs, \
    billing_tariff


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
    except Exception as e:
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

    ctx = {'data': [], 'query': ''}

    if request.method == 'POST':
        query = request.POST['query']
        ctx['query'] = query

        try:
            ctx['data'] = async_movies_search(access_token, query)
        except Exception as e:
            ctx['errors'] = str(e)

    return render(request, 'movies.html', ctx)


def movies_detail(request, movies_id):
    """Информация о фильме"""
    access_token = request.session.get('access_token')
    if not access_token:
        return HttpResponseRedirect(reverse('demo:login'))

    ctx = {'data': []}

    try:
        ctx['data'] = async_movies_detail(access_token, movies_id)
    except Exception as e:
        ctx['errors'] = str(e)

    return render(request, 'movies_detail.html', ctx)


def tariffs(request):
    """Подписки"""
    access_token = request.session.get('access_token')
    if not access_token:
        return HttpResponseRedirect(reverse('demo:login'))
    ctx = {'data': []}

    try:
        ctx['data'] = billing_tariffs(access_token)
    except Exception as e:
        ctx['errors'] = str(e)

    return render(request, 'tariffs.html', ctx)


def tariff(request, tariff_id):
    """Оформить подписку"""
    access_token = request.session.get('access_token')
    if not access_token:
        return HttpResponseRedirect(reverse('demo:login'))
    ctx = {'data': []}

    try:
        ctx['data'] = billing_tariff(access_token, tariff_id)
    except Exception as e:
        ctx['errors'] = str(e)

    return render(request, 'tariff.html', ctx)
