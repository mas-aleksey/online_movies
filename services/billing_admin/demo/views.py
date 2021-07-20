from functools import wraps

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from demo.forms import LoginForm
from demo.services import auth_profile, auth_logout, async_movies_search, async_movies_detail, billing_tariffs, \
    billing_tariff, billing_order, billing_subscribe, auth_access_check, billing_subscriptions


def index(request):
    access_token = request.session.get('access_token', '')
    if not access_token:
        return HttpResponseRedirect(reverse('demo:login'))
    return HttpResponseRedirect(reverse('demo:profile'))


def check_token(view_func):
    """Проверка валидности токена."""

    def wrapped_view(request, **kwargs):
        access_token = request.session.get('access_token')
        if not access_token or not auth_access_check(access_token):
            return HttpResponseRedirect(reverse('demo:login'))
        return view_func(request, **kwargs)

    return wraps(view_func)(wrapped_view)


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


@check_token
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


@check_token
def movies(request):
    """доступные фильмы"""
    access_token = request.session.get('access_token')
    ctx = {'data': [], 'query': ''}

    if request.method == 'POST':
        query = request.POST['query']
        ctx['query'] = query

        try:
            ctx['data'] = async_movies_search(access_token, query)
        except Exception as e:
            ctx['errors'] = str(e)

    return render(request, 'movies.html', ctx)


@check_token
def movies_detail(request, movies_id):
    """Информация о фильме"""
    access_token = request.session.get('access_token')
    ctx = {'data': []}

    try:
        ctx['data'] = async_movies_detail(access_token, movies_id)
    except Exception as e:
        ctx['errors'] = str(e)

    return render(request, 'movies_detail.html', ctx)


@check_token
def tariffs(request):
    """Подписки"""
    access_token = request.session.get('access_token')
    ctx = {'data': []}

    try:
        ctx['data'] = billing_tariffs(access_token)
    except Exception as e:
        ctx['errors'] = str(e)

    return render(request, 'tariffs.html', ctx)


@check_token
def tariff(request, tariff_id):
    """Оформить подписку"""
    access_token = request.session.get('access_token')
    ctx = {'data': []}

    try:
        ctx['data'] = billing_tariff(access_token, tariff_id)
    except Exception as e:
        ctx['errors'] = str(e)

    return render(request, 'tariff.html', ctx)


@check_token
def order(request, tariff_id):
    """оплата подписки"""

    access_token = request.session.get('access_token')
    ctx = {'data': []}

    try:
        ctx['data'] = billing_order(access_token, tariff_id)
    except Exception as e:
        ctx['errors'] = str(e)
        return render(request, '500.html', ctx)

    return HttpResponseRedirect(ctx['data']['confirmation_url'])


@check_token
def subscriptions(request):
    """мои подписки"""

    access_token = request.session.get('access_token')
    ctx = {'data': []}

    try:
        ctx['data'] = billing_subscriptions(access_token)
    except Exception as e:
        ctx['errors'] = str(e)
        return render(request, '500.html', ctx)

    return render(request, 'subscriptions.html', ctx)


@check_token
def subscribe(request, subscribe_id):
    """статус подписки"""

    refresh_page = request.GET.get('refresh_page', "0")
    access_token = request.session.get('access_token')
    ctx = {
        'data': [],
        'refresh_page': refresh_page
    }

    try:
        ctx['data'] = billing_subscribe(access_token, subscribe_id)
    except Exception as e:
        ctx['errors'] = str(e)
        return render(request, '500.html', ctx)

    return render(request, 'subscribe.html', ctx)
