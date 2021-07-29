import random

import settings

user_agent = str(random.randint(1, 999999))


def get_auth_access_token(client) -> str:
    """Получить админский токен в auth."""
    url = f'{settings.AUTH_SERVER}/api/v1/auth/login'
    headers = {
        'content-type': 'application/json',
        'user-agent': user_agent
    }
    data = {
        "email": settings.AUTH_ADMIN,
        "password": settings.AUTH_PASSWORD
    }
    r = client.post(url, json=data, headers=headers)
    r.raise_for_status()
    return r.json()['access_token']


def revoke_auth_user_access_token(client, admin_token: str, user_id: str):
    """Удалить действующий токен пользователя, чтобы в нем обновились роли."""
    url = f'{settings.AUTH_SERVER}/api/v1/users/{user_id}/revoke_access_keys'
    headers = {
        'content-type': 'application/json',
        'authorization': f'Bearer {admin_token}',
        'user-agent': user_agent
    }

    r = client.get(url, headers=headers)


def change_auth_user_role(client, method, user_id: str, roles: list):
    """Добавить/удалить роль пользователю."""
    token = get_auth_access_token(client)
    url = f'{settings.AUTH_SERVER}/api/v1/users/{user_id}/roles'
    headers = {
        'content-type': 'application/json',
        'authorization': f'Bearer {token}',
        'user-agent': user_agent
    }
    for role in roles:
        if method == 'post':
            r = client.post(url, json={"role": role}, headers=headers)
        else:
            r = client.delete(url, json={"role": role}, headers=headers)

    revoke_auth_user_access_token(client, token, user_id)


def add_auth_user_role(client, user_id: str, roles: list):
    """Добавить роли для пользователю."""
    change_auth_user_role(client, 'post', user_id, roles)


def delete_auth_user_role(client, user_id: str, roles: list):
    """Удалить роли у пользователя."""
    change_auth_user_role(client, 'delete', user_id, roles)
