import requests
from requests import HTTPError

import settings


def auth_login(client, login, password):
    url = f'{settings.AUTH_BASE_URL}/api/v1/auth/login'
    headers = {'content-type': 'application/json', 'user-agent': 'billing'}
    payload = {
        "email": login,
        "password": password
    }
    resp = client.post(
        url=url,
        json=payload,
        headers=headers,

    )
    access_token = resp.json()['access_token']
    refresh_token = resp.json()['refresh_token']
    headers['authorization'] = f'Bearer {access_token}'
    headers['access_token'] = access_token
    headers['refresh_token'] = refresh_token
    client.headers = headers
    return client


def auth_signup(client, login, password):
    url = f'{settings.AUTH_BASE_URL}/api/v1/auth/signup'
    headers = {'content-type': 'application/json', 'user-agent': 'billing'}
    payload = {
        "email": login,
        "password": password
    }
    resp = client.post(
        url=url,
        json=payload,
        headers=headers,
    )
    return client


def auth_logout(client):
    url = f'{settings.AUTH_BASE_URL}/api/v1/auth/logout'
    client.delete(url=url)


def auth_refresh(client):
    url = f'{settings.AUTH_BASE_URL}/api/v1/auth/refresh'
    refresh_token = client.headers['refresh_token']
    headers = {'content-type': 'application/json', 'user-agent': 'billing', 'authorization': f'Bearer {refresh_token}'}
    resp = client.post(
        url=url,
        headers=headers,
    )

    access_token = resp.json()['access_token']
    refresh_token = resp.json()['refresh_token']
    headers['authorization'] = f'Bearer {access_token}'
    headers['access_token'] = access_token
    headers['refresh_token'] = refresh_token
    client.headers = headers

    return client


def auth_access_check(access_token):
    url = f'{settings.AUTH_BASE_URL}/api/v1/auth/access_check'
    headers = {'content-type': 'application/json', 'user-agent': 'billing', 'authorization': f'Bearer {access_token}'}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return True
    return False


def auth_profile(client):
    url = f'{settings.AUTH_BASE_URL}/api/v1/auth/access_check'
    scope = {}

    resp = client.get(url)
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


def async_movies_search(client, query):
    url = f'{settings.ASYNC_BASE_URL}/api/v1/film/search?limit=50&page=1&query={query}'
    resp = client.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data

    raise HTTPError(resp.text)


def async_movies_detail(client, movies_id):
    url = f'{settings.ASYNC_BASE_URL}/api/v1/film/{movies_id}'
    resp = client.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data

    raise HTTPError(resp.text)


def billing_products(client):
    url = f'{settings.BILLING_BASE_URL}/subscription/v1/products/'
    resp = client.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data

    raise HTTPError(resp.text)


def billing_order(client, tariff_id, payment_system):
    url = f'{settings.BILLING_BASE_URL}/subscription/v1/order/'
    payload = {
        "tariff_id": tariff_id,
        "payment_system": payment_system
    }
    resp = client.post(
        url=url,
        json=payload,
    )
    if resp.status_code == 200:
        data = resp.json()
        return data

    raise HTTPError(resp.text)


def billing_subscriptions(client):
    url = f'{settings.BILLING_BASE_URL}/subscription/v1/subscriptions/'
    resp = client.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data

    raise HTTPError(resp.text)


def billing_subscription(client, subscription_id):
    url = f'{settings.BILLING_BASE_URL}/subscription/v1/subscriptions/{subscription_id}'
    resp = client.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data

    raise HTTPError(resp.text)


def billing_tariff(client, tariff_id):
    url = f'{settings.BILLING_BASE_URL}/subscription/v1/tariff/{tariff_id}'
    resp = client.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data

    raise HTTPError(resp.text)
