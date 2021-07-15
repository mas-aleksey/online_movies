from flask import Flask
from typing import Tuple
from flask_jwt_extended import JWTManager, get_jti, create_access_token, create_refresh_token

from src.models.db_models import User
from src.storage.redis import redis_db, save_tokens
from src.settings import JWT_SECRET_KEY, ACCESS_EXPIRES, REFRESH_EXPIRES

jwt = JWTManager()


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token_in_redis = redis_db.get(jti)
    return token_in_redis == b'revoked'


def init_jwt(app: Flask):
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = REFRESH_EXPIRES
    jwt.init_app(app)


def genetare_tokens(user: User, user_agent: str) -> Tuple[str, str]:
    user_id = str(user.id)
    user_extra = {
        'superuser': user.superuser,
        'roles': [role.name for role in user.roles],
        'user_id': user_id
    }
    access_token = create_access_token(identity=user_id, expires_delta=ACCESS_EXPIRES, additional_claims=user_extra)
    refresh_token = create_refresh_token(identity=user_id, expires_delta=REFRESH_EXPIRES)
    save_tokens(
        user_id=user_id,
        access_jti=get_jti(access_token),
        refresh_jti=get_jti(refresh_token),
        user_agent=user_agent
    )
    return access_token, refresh_token
