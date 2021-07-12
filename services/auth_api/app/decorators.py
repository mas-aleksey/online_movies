from functools import wraps

from flask_jwt_extended import get_jwt_identity
from flask_restful import abort

from app.models import User


def is_superuser(fn):
    """Проверят наличие прав супер пользователя"""

    @wraps(fn)
    def decorator(*args, **kwargs):
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()
        if not user.is_superuser:
            raise abort(400, message='Недостаточно прав.')
        return fn(*args, **kwargs)

    return decorator
