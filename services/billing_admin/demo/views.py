from functools import wraps

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from requests import RequestException
from demo.forms import LoginForm
from demo.services import (
    auth_profile, auth_logout, async_movies_search, async_movies_detail,
    billing_tariff, billing_order, billing_subscribe, auth_access_check,
    billing_subscriptions, billing_products, billing_unsubscribe, auth_refresh
)


def index(request):
    access_token = request.session.get('access_token', '')
    if not access_token:
        return HttpResponseRedirect(reverse('demo:login'))
    return HttpResponseRedirect(reverse('demo:profile'))


def check_token(view_func):
    """Проверка валидности токена."""

    def wrapped_view(request, **kwargs):
        access_token = request.session.get('access_token')
        refresh_token = request.session.get('refresh_token')

        if not access_token or not refresh_token:
            return HttpResponseRedirect(reverse('demo:login'))

        if not auth_access_check(access_token):
            try:
                tokens = auth_refresh(refresh_token)
            except:
                request.session['access_token'] = None
                request.session['refresh_token'] = None
                return HttpResponseRedirect(reverse('demo:login'))

            request.session['access_token'] = tokens['access_token']
            request.session['refresh_token'] = tokens['refresh_token']

        return view_func(request, **kwargs)

    return wraps(view_func)(wrapped_view)


def login(request):
    """Логин."""
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
    """Профиль пользователя."""

    access_token = request.session.get('access_token')
    if not access_token:
        return HttpResponseRedirect(reverse('demo:login'))

    ctx = {}
    try:
        ctx = auth_profile(access_token)
    except RequestException as e:
        ctx['errors'] = str(e)

    ctx['access_token'] = access_token
    ctx['refresh_token'] = request.session.get('refresh_token')

    return render(request, 'profile.html', ctx)


def logout(request):
    """Выход пользователя."""
    access_token = request.session.get('access_token', '')

    if access_token:
        request.session['access_token'] = None
        request.session['refresh_token'] = None

    auth_logout(access_token)

    return HttpResponseRedirect(reverse('demo:login'))


@check_token
def movies(request):
    """Доступные фильмы."""
    access_token = request.session.get('access_token')
    ctx = {'data': [], 'query': ''}

    if request.method == 'POST':
        query = request.POST['query']
        ctx['query'] = query

        try:
            ctx['data'] = async_movies_search(access_token, query)
        except RequestException as e:
            ctx['errors'] = str(e)

    return render(request, 'movies.html', ctx)


@check_token
def movies_detail(request, movies_id):
    """Информация о фильме."""
    access_token = request.session.get('access_token')
    ctx = {'data': []}

    try:
        ctx['data'] = async_movies_detail(access_token, movies_id)
    except RequestException as e:
        ctx['errors'] = str(e)

    return render(request, 'movies_detail.html', ctx)


@check_token
def products(request):
    """Продукты."""
    access_token = request.session.get('access_token')
    ctx = {'data': []}

    try:
        ctx['data'] = billing_products(access_token)
    except RequestException as e:
        ctx['errors'] = str(e)

    return render(request, 'products.html', ctx)


@check_token
def tariff(request, tariff_id):
    """Оформить подписку."""
    access_token = request.session.get('access_token')
    ctx = {'data': []}

    try:
        ctx['data'] = billing_tariff(access_token, tariff_id)
    except RequestException as e:
        ctx['errors'] = str(e)

    return render(request, 'tariff.html', ctx)


@check_token
def order(request):
    """Оплата подписки."""
    if not request.POST:
        return render(request, '500.html', {'errors': 'Something went wrong'})

    tariff_id = request.POST.get('tariff_id')
    payment_system = request.POST.get('payment_system')
    access_token = request.session.get('access_token')
    ctx = {'data': []}

    try:
        ctx['data'] = billing_order(access_token, tariff_id, payment_system)
    except RequestException as e:
        ctx['errors'] = str(e)
        return render(request, '500.html', ctx)

    return HttpResponseRedirect(ctx['data']['confirmation_url'])  # noqa


@check_token
def subscriptions(request):
    """Мои подписки."""

    access_token = request.session.get('access_token')
    ctx = {'data': []}

    try:
        ctx['data'] = billing_subscriptions(access_token)
    except RequestException as e:
        ctx['errors'] = str(e)
        return render(request, '500.html', ctx)

    return render(request, 'subscriptions.html', ctx)


@check_token
def subscribe(request, subscribe_id):
    """Статус подписки."""

    refresh_page = request.GET.get('refresh_page', "0")
    access_token = request.session.get('access_token')
    ctx = {
        'data': [],
        'refresh_page': refresh_page
    }

    try:
        ctx['data'] = billing_subscribe(access_token, subscribe_id)
    except RequestException as e:
        ctx['errors'] = str(e)
        return render(request, '500.html', ctx)

    return render(request, 'subscribe.html', ctx)


@check_token
def unsubscribe(request, subscribe_id):
    """Отмена подписки."""

    access_token = request.session.get('access_token')

    try:
        billing_unsubscribe(access_token, subscribe_id)
    except RequestException as e:
        ctx = {'errors': str(e)}
        return render(request, '500.html', ctx)

    return HttpResponseRedirect(reverse('demo:subscribe', args=(subscribe_id,)) + "?refresh_page=1")
