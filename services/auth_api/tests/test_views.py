import datetime

from oauth.yandex import OauthToken, OauthUser

BASE_URL = 'http://localhost:5000/api/v1'


def get_tokens(client):
    # регистрация
    data = {
        "email": "test1@email.example",
        "password": "test_password",
        "recaptcha": "recaptcha_key"
    }
    client.post(f'{BASE_URL}/user/registration', json=data)

    # логин
    rv = client.post(f'{BASE_URL}/login', json=data)

    return rv.json


def test_registration_user(client) -> None:
    data = {
        "email": "test1@email.example",
        "password": "test_password",
        "recaptcha": "recaptcha_key"
    }

    rv = client.post(f'{BASE_URL}/user/registration', json=data)
    assert rv.json == {'email': 'test1@email.example'}


def test_login(client) -> None:
    data = {
        "email": "test1@email.example",
        "password": "test_password",
        "recaptcha": "recaptcha_key"
    }
    client.post(f'{BASE_URL}/user/registration', json=data)
    rv = client.post(f'{BASE_URL}/login', json=data)
    assert 'access_token' in rv.json
    assert 'refresh_token' in rv.json


def test_change_password(client) -> None:
    tokens = get_tokens(client)

    # смена пароля
    password_data = {
        "password": "test_password",
        "new_password": "new_password",
    }
    headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
    rv = client.post(f'{BASE_URL}/user/password', json=password_data, headers=headers)
    assert rv.status_code == 200

    # логин с новым паролем
    data = {
        "email": "test1@email.example",
        "password": password_data['new_password'],
        "recaptcha": "recaptcha_key"
    }
    rv = client.post(f'{BASE_URL}/login', json=data)
    assert rv.status_code == 200
    assert 'access_token' in rv.json
    assert 'refresh_token' in rv.json


def test_refresh_token(client) -> None:
    tokens = get_tokens(client)

    # смена токена
    refresh_data = {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
    }
    headers = {'Authorization': f'Bearer {tokens["refresh_token"]}'}
    rv = client.post(f'{BASE_URL}/token/refresh', json=refresh_data, headers=headers)
    assert rv.status_code == 200
    assert refresh_data['access_token'] != rv.json['access_token']
    assert refresh_data['refresh_token'] != rv.json['refresh_token']


def test_view_journal(client) -> None:
    tokens = get_tokens(client)

    # просмотр журнала
    headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
    rv = client.get(f'{BASE_URL}/user/journal/login', headers=headers)
    assert rv.status_code == 200
    assert len(rv.json) == 1
    assert 'logined_by' in rv.json[0]
    assert 'user_agent' in rv.json[0]


def test_check_token(client) -> None:
    tokens = get_tokens(client)

    # проверка токена
    headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
    rv = client.get(f'{BASE_URL}/token/verify', headers=headers)
    assert rv.status_code == 200
    assert rv.json == True

    # токен не действителен
    headers = {'Authorization': f'Bearer 123'}
    rv = client.get(f'{BASE_URL}/token/verify', headers=headers)
    assert rv.status_code == 422


def test_logout(client) -> None:
    tokens = get_tokens(client)
    headers = {'Authorization': f'Bearer {tokens["access_token"]}'}

    # токен действителен
    rv = client.get(f'{BASE_URL}/token/verify', headers=headers)
    assert rv.status_code == 200

    # выход
    rv = client.get(f'{BASE_URL}/logout', headers=headers)
    assert rv.status_code == 200

    # токен не действителен
    rv = client.get(f'{BASE_URL}/token/verify', headers=headers)
    assert rv.status_code == 401


def test_ya_authorized(client, monkeypatch) -> None:
    monkeypatch.setattr(
        'app.service.get_ya_user_info',
        lambda access_token: OauthUser(social_id='100', email='ya_user@example.mail')
    )
    monkeypatch.setattr(
        'oauth.yandex._get_tokens',
        lambda data: OauthToken(access_token='access_token',
                                refresh_token='refresh_token',
                                expires=datetime.datetime.now())
    )

    # вход с помощью соцсети
    rv = client.get(f'{BASE_URL}/oauth/ya_authorized?code=999')
    assert rv.status_code == 200
    tokens = rv.json
    headers = {'Authorization': f'Bearer {tokens["access_token"]}'}

    # токен действителен
    rv = client.get(f'{BASE_URL}/token/verify', headers=headers)
    assert rv.status_code == 200
