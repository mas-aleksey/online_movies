from flask import Blueprint, jsonify, request
from flasgger import swag_from

from src.api.utils import super_jwt_required
from src.models.db_models import User, Role
from src.models.schemas import RoleSchema
from src.storage.postgres import db
from src.storage.redis import revoke_access_tokens
from src.settings import DOCS_DIR


users_api = Blueprint('users', __name__)


@users_api.route('<user_id>/roles', methods=['GET'])
@super_jwt_required
@swag_from(DOCS_DIR.joinpath('users').joinpath('get_user_roles.yml'))
def get_user_roles(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify(msg='user does not exist'), 409

    return jsonify(roles=[r.name for r in user.roles])


@users_api.route('<user_id>/roles', methods=['POST'])
@super_jwt_required
@swag_from(DOCS_DIR.joinpath('users').joinpath('add_role_to_user.yml'))
def add_role_to_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify(msg='user does not exist'), 409

    schema = RoleSchema()
    data = schema.flask_load(request.json)
    role_name = data['role']
    role = Role.get_by_name(role_name)

    if not role:
        return jsonify(msg='roles does not exist'), 409

    if role in user.roles:
        return jsonify(msg='user already has role'), 409

    user.roles.append(role)
    db.session.commit()
    return jsonify(msg='success added')


@users_api.route('<user_id>/roles', methods=['DELETE'])
@super_jwt_required
@swag_from(DOCS_DIR.joinpath('users').joinpath('delete_user_role.yml'))
def delete_user_role(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify(msg='user does not exist'), 409

    schema = RoleSchema()
    data = schema.flask_load(request.json)
    role_name = data['role']
    role = Role.get_by_name(role_name)

    if not role:
        return jsonify(msg='roles does not exist'), 409

    if role not in user.roles:
        return jsonify(msg='user has not role'), 409

    user.roles.remove(role)
    db.session.commit()
    return jsonify(msg='success deleted')


@users_api.route('<user_id>/superuser', methods=['GET'])
@super_jwt_required
@swag_from(DOCS_DIR.joinpath('users').joinpath('super_user.yml'))
def super_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify(msg='user does not exist'), 409

    if user.superuser:
        return jsonify(msg='user already is superuser'), 409

    user.superuser = True
    db.session.commit()
    return jsonify(msg='succeed superuser granted')


@users_api.route('<user_id>/revoke_access_keys', methods=['GET'])
@super_jwt_required
@swag_from(DOCS_DIR.joinpath('users').joinpath('revoke_access_keys.yml'))
def revoke_access_keys(user_id):
    count = revoke_access_tokens(user_id)
    return jsonify(msg=f'{count} token(s) has revoked')
