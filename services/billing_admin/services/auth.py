import requests
from django.conf import settings


def get_auth_access_token() -> str:
    """Получить админский токен в auth"""
    url = f'{settings.AUTH_SERVER}/api/v1/auth/login'
    headers = {
        'content-type': 'application/json'
    }
    data = {
        "email": settings.AUTH_ADMIN,
        "password": settings.AUTH_PASSWORD
    }
    r = requests.post(url, json=data, headers=headers)
    r.raise_for_status()
    return r.json()['access_token']


def revoke_auth_user_access_token(admit_token: str, user_id: str):
    """Удалить действующий токен пользователя, чтобы в нем обновились роли."""
    url = f'{settings.AUTH_SERVER}/api/v1/users/{user_id}/revoke_access_keys'
    headers = {
        'content-type': 'application/json',
        'authorization': f'Bearer {admit_token}'
    }

    r = requests.get(url, headers=headers)
    r.raise_for_status()


def change_auth_user_role(method, user_id: str, access_type: str):
    """Добавить/удалить роль пользователю."""
    token = get_auth_access_token()
    url = f'{settings.AUTH_SERVER}/api/v1/users/{user_id}/roles'
    headers = {
        'content-type': 'application/json',
        'authorization': f'Bearer {token}'
    }

    data = {
        "role": access_type
    }

    r = requests.request(method, url, json=data, headers=headers)
    if r.status_code not in [200, 409]:
        r.raise_for_status()

    revoke_auth_user_access_token(token, user_id)


def add_auth_user_role(user_id: str, access_type: str):
    """Добавить роль пользователю."""
    change_auth_user_role('post', user_id, access_type)


def delete_auth_user_role(user_id: str, access_type: str):
    """Удалить роль пользователя."""
    change_auth_user_role('delete', user_id, access_type)
