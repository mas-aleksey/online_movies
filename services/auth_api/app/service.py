import datetime
import uuid
from typing import Optional

import pytz
from flask_jwt_extended import create_access_token, create_refresh_token

from app import redis_db, jwt, db, app
from app.models import UserSignIn, User, OauthUser
from oauth.base import OauthUserDataclass, BaseOAuthService
from oauth.yandex import YaOAuthProvider


def add_token_to_blacklist(jwt_payload) -> None:
    """Добавляет токен в blacklist"""

    user = jwt_payload['sub']
    token = jwt_payload['jti']
    now_time = datetime.datetime.now()
    exp_time = datetime.datetime.fromtimestamp(jwt_payload["exp"])
    redis_db.set(f'{user}:{token}', "", ex=exp_time - now_time)


def get_user_claims(email: str) -> dict:
    """Полезная нагрузка токена."""

    user = User.query.filter_by(email=email).first()
    if not user:
        return {}

    data = {
        'roles': [role.name for role in user.roles],
        'is_superuser': user.is_superuser
    }
    return data


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload) -> bool:
    """Проверка токена на вхождение в черный список."""

    user = jwt_payload['sub']
    token = jwt_payload['jti']
    device = jwt_payload['device']
    session = jwt_payload['session']
    token_in_redis = redis_db.get(f'{user}:{token}')
    session_in_redis = redis_db.get(f'{user}:{device}:{session}')  # если был logout
    return token_in_redis is not None or session_in_redis is not None


def user_logout_by_device(user: User, device: str) -> None:
    """Выход из всех сессий на устройстве.
    Ищет все недавние, неистекшие сессии входа на устройстве
    и добавляет их в черный список.
    """

    token_timeout = app.config.get('JWT_REFRESH_TOKEN_EXPIRES')
    now_time = datetime.datetime.now(pytz.utc)

    # берем все логины на устройстве, сессии которых еще могут быть активными
    signs = UserSignIn.query \
        .filter_by(user_id=user.id, user_agent=device) \
        .filter(UserSignIn.logined_by > now_time - token_timeout).all()

    for sign in signs:
        exp_time = sign.logined_by.replace(tzinfo=pytz.utc) + token_timeout
        exp_time = exp_time.replace(tzinfo=pytz.utc)

        # добавляем в черный список
        redis_db.set(f'{user.email}:{device}:{sign.id}', "", ex=exp_time - now_time)


def create_tokens(user: User, device: str) -> dict:
    """Создание токена для устройства."""

    # Предварительно завершаем все предыдущие сессии
    user_logout_by_device(user, device)

    sign_in = UserSignIn(user_id=user.id, user_agent=device, user_device_type=device.split('/')[0])
    db.session.add(sign_in)
    db.session.commit()

    token_params = {
        'additional_claims': {"device": device, 'session': sign_in.id, **get_user_claims(user.email)},
        'identity': user.email
    }

    access_token = create_access_token(**token_params)
    refresh_token = create_refresh_token(**token_params)

    tokens = {'access_token': access_token, 'refresh_token': refresh_token}
    return tokens


def refresh_tokens(jwt_payload: dict) -> dict:
    """Обновление токенов."""

    # refresh токен добавляем в черный список, таким образом делаем его одноразовым.
    add_token_to_blacklist(jwt_payload)

    user = jwt_payload['sub']
    device = jwt_payload['device']
    session = jwt_payload['session']

    token_params = {
        'additional_claims': {"device": device, 'session': session, **get_user_claims(user)},
        'identity': user
    }

    access_token = create_access_token(**token_params)
    refresh_token = create_refresh_token(**token_params)

    tokens = {'access_token': access_token, 'refresh_token': refresh_token}
    return tokens


def get_user_by_credentials(email: str, password: str) -> Optional[User]:
    """Ищет пользователя по email и проверяет соответствие пароля. """

    user = User.query.filter_by(email=email).first()

    if not user or (user and not user.verify_password(password)):
        return None

    return user


def get_or_create_oauth_user(oauth_user: OauthUserDataclass) -> User:
    """Авторизация пользователя через соцсеть"""

    ya_user = OauthUser.query.filter_by(social_id=oauth_user.social_id).first()

    if ya_user and ya_user.user_id:
        return User.query.filter_by(id=ya_user.user_id).first()

    user = User.query.filter_by(email=oauth_user.email).first()
    if not user:
        user = User(email=oauth_user.email, password=str(uuid.uuid4()))
        db.session.add(user)
        db.session.commit()

    if not ya_user:
        ya_user = OauthUser(user_id=user.id, social_id=oauth_user.social_id, social_name=oauth_user.social_name)
        db.session.add(ya_user)

    if not ya_user.user_id:
        ya_user.user_id = user.id

    db.session.commit()
    return user


class OAuthService(BaseOAuthService):
    providers_class = [YaOAuthProvider]
