import requests

from app import app
from oauth.base import BaseOAuthProvider, OauthUserDataclass


class YaOAuthProvider(BaseOAuthProvider):
    """Провайдер яндекс авторизации"""
    name = 'yandex'
    INFO_URL = 'https://login.yandex.ru/info?format=json'
    BASE_OAUTH_URL = 'https://oauth.yandex.ru'

    def __init__(self) -> None:
        self.YA_CLIENT_ID = app.config.get('YA_CLIENT_ID')
        self.YA_CLIENT_SECRET = app.config.get('YA_CLIENT_SECRET')
        super().__init__()

    def _get_token(self, code: str) -> str:
        """Получить access_token для пользователя яндекс по коду авторизации"""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.YA_CLIENT_ID,
            "client_secret": self.YA_CLIENT_SECRET
        }
        url = f'{self.BASE_OAUTH_URL}/token'
        response = requests.post(url, data=data)
        data = response.json()
        return data['access_token']

    def _get_user_info(self, code: str) -> OauthUserDataclass:
        """Возвращает информацию по пользователю"""
        access_token = self._get_token(code)
        headers = {'Authorization': f'OAuth {access_token}'}
        response = requests.get(self.INFO_URL, headers=headers)
        info = response.json()
        return OauthUserDataclass(social_id=info['id'], email=info['default_email'], social_name=self.name)

    def get_login_url(self) -> str:
        url = f'{self.BASE_OAUTH_URL}/authorize?response_type=code&client_id={self.YA_CLIENT_ID}'
        return url

    def callback(self, request) -> OauthUserDataclass:
        code = request.args.get('code')
        return self._get_user_info(code)
