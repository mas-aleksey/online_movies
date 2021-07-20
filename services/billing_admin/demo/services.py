import requests
from django.conf import settings
from requests import HTTPError

AUTH_BASE_URL = settings.AUTH_SERVER
BILLING_BASE_URL = 'https://yandexmovies.online/billing'
# BILLING_BASE_URL = 'http://127.0.0.1:8000/billing'


def auth_login(login, password):
    url = f'{AUTH_BASE_URL}/api/v1/auth/login'
    headers = {'content-type': 'application/json', 'user-agent': 'billing'}
    payload = {
        "email": login,
        "password": password
    }
    resp = requests.post(
        url=url,
        json=payload,
        headers=headers,

    )
    try:
        resp.raise_for_status()
    except HTTPError:
        raise HTTPError(resp.text)

    return resp.json()


def auth_logout(access_token):
    url = f'{AUTH_BASE_URL}/api/v1/auth/logout'
    headers = {'content-type': 'application/json', 'user-agent': 'billing', 'authorization': f'Bearer {access_token}'}
    requests.delete(url=url, headers=headers, )


def auth_refresh(refresh_token):
    url = f'{AUTH_BASE_URL}/api/v1/auth/refresh'
    headers = {'content-type': 'application/json', 'user-agent': 'billing', 'authorization': f'Bearer {refresh_token}'}
    resp = requests.post(
        url=url,
        headers=headers,
    )

    try:
        resp.raise_for_status()
    except HTTPError:
        raise HTTPError(resp.text)

    return resp.json()


def auth_profile(refresh_token):
    tokens = auth_refresh(refresh_token)
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']

    url = f'{AUTH_BASE_URL}/api/v1/auth/access_check'
    headers = {'content-type': 'application/json', 'user-agent': 'billing', 'authorization': f'Bearer {access_token}'}
    scope = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }

    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        scope['is_superuser'] = data.get('is_super') or False
        scope['user_roles'] = list(data.get('roles') or [])
        scope['user_id'] = data.get('user_id') or None
        scope['email'] = data.get('email') or None
    try:
        resp.raise_for_status()
    except HTTPError:
        raise HTTPError(resp.text)

    return scope


def async_movies_search(access_token, query):
    url = f'{settings.ASYNC_SERVER}/api/v1/film/search?limit=50&page=1&query={query}'
    headers = {'content-type': 'application/json', 'user-agent': 'billing', 'authorization': f'Bearer {access_token}'}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return data

    raise HTTPError(resp.text)


def async_movies_detail(access_token, movies_id):
    url = f'{settings.ASYNC_SERVER}/api/v1/film/{movies_id}'
    headers = {'content-type': 'application/json', 'user-agent': 'billing', 'authorization': f'Bearer {access_token}'}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return data

    raise HTTPError(resp.text)


def billing_tariffs(access_token):
    url = f'{BILLING_BASE_URL}/subscription/v1/tariffs/'
    headers = {'content-type': 'application/json', 'user-agent': 'billing', 'authorization': f'Bearer {access_token}'}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return data

    raise HTTPError(resp.text)


def billing_tariff(access_token, tariff_id):
    url = f'{BILLING_BASE_URL}/subscription/v1/tariff/{tariff_id}'
    headers = {'content-type': 'application/json', 'user-agent': 'billing', 'authorization': f'Bearer {access_token}'}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return data

    raise HTTPError(resp.text)


def billing_order(access_token, tariff_id):
    url = f'{BILLING_BASE_URL}/subscription/v1/order/'
    headers = {'content-type': 'application/json', 'user-agent': 'billing', 'authorization': f'Bearer {access_token}'}
    payload = {
        "tariff_id": tariff_id,
        "payment_system": 'yoomoney'
    }
    resp = requests.post(
        url=url,
        json=payload,
        headers=headers,

    )
    if resp.status_code == 200:
        data = resp.json()
        return data

    raise HTTPError(resp.text)
