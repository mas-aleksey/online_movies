import logging

import requests
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(MiddlewareMixin):
    """Проверка аутентификации пользователя."""

    def process_request(self, request):
        is_superuser = False
        roles = {'free'}
        user_id = None
        email = None
        token = request.COOKIES.get('authorization') or request.headers.get("authorization")
        headers = {
            'authorization': token,
            'user-agent': request.headers["user-agent"]
        }
        try:
            if not token:
                raise ValueError('TOKEN is empty')
            resp = requests.get(settings.AUTH_ENDPOINT, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                is_superuser = data.get('is_super') or False
                user_roles = data.get('roles') or []
                user_id = data.get('user_id') or None
                email = data.get('email') or None
                roles.update(user_roles)
        except Exception as exc:
            logger.error(exc)
        else:
            logger.info('response %s %s', resp.status_code, resp.text)

        request.scope = {
            "is_superuser": is_superuser,
            "roles": list(roles),
            "user_id": user_id,
            "email": email
        }
