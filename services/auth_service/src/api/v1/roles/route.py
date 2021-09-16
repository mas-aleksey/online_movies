from flask import Blueprint, jsonify, request
from flasgger import swag_from

from src.models.db_models import Role
from src.models.schemas import RoleSchema, RolePathSchema
from src.api.utils import super_jwt_required
from src.storage.postgres import db
from src.settings import DOCS_DIR


roles_api = Blueprint('roles', __name__)


@roles_api.route('/', methods=['GET'])
@super_jwt_required
@swag_from(DOCS_DIR.joinpath('roles').joinpath('get_roles.yml'))
def get_roles():
    roles = Role.query.all()
    return jsonify(roles=[r.name for r in roles])


@roles_api.route('/', methods=['POST'])
@super_jwt_required
@swag_from(DOCS_DIR.joinpath('roles').joinpath('add_new_role.yml'))
def add_new_role():
    schema = RoleSchema()
    data = schema.flask_load(request.json)
    role_name = data['role']

    if Role.get_by_name(role_name):
        return jsonify(msg='roles already exist'), 409

    db.session.add(Role(role_name))
    db.session.commit()
    return jsonify(msg='sucess added')


@roles_api.route('/', methods=['PATCH'])
@super_jwt_required
@swag_from(DOCS_DIR.joinpath('roles').joinpath('patch_role.yml'))
def patch_role():
    schema = RolePathSchema()
    data = schema.flask_load(request.json)

    role = Role.get_by_name(data['old_role'])
    if role:
        role.name = data['new_role']
        db.session.commit()
        return jsonify(msg='sucess patched')
    return jsonify(msg='roles does not exist'), 409


@roles_api.route('/', methods=['DELETE'])
@super_jwt_required
@swag_from(DOCS_DIR.joinpath('roles').joinpath('delete_role.yml'))
def delete_role():
    schema = RoleSchema()
    data = schema.flask_load(request.json)

    is_delete = Role.query.filter_by(name=data['role']).delete()
    db.session.commit()
    if is_delete:
        return jsonify(msg='success deleted')
    return jsonify(msg='roles does not exist'), 409
