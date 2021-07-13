from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt


def super_jwt_required(func):
    @wraps(func)
    @jwt_required()
    def inner(*args, **kwargs):
        is_super = get_jwt()["superuser"]
        if not is_super:
            return jsonify(msg='Superuser required'), 401
        return func(*args, **kwargs)
    return inner
