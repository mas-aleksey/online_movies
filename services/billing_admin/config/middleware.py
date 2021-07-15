import logging

import requests
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

LOGGER = logging.getLogger(__name__)


class AuthenticationMiddleware(MiddlewareMixin):
    """Проверка аутентификации пользователя"""

    def process_request(self, request):
        is_superuser = False
        roles = {'free'}
        user_id = None
        headers = {
            'authorization': request.headers["authorization"],
            'user-agent': request.headers["user-agent"]
        }
        try:
            resp = requests.get(settings.AUTH_ENDPOINT, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                is_superuser = data.get('is_super') or False
                user_roles = data.get('roles') or []
                user_id = data.get('user_id') or None
                roles.update(user_roles)
        except Exception as exc:
            LOGGER.error(exc)

        request.scope = {
            "is_superuser": is_superuser,
            "roles": list(roles),
            "user_id": user_id
        }
