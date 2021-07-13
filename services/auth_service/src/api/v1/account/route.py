from typing import List
from flask import Blueprint, jsonify, request
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.models.db_models import User, UserSignIn
from src.models.schemas import PatchLogin, PatchPassword
from src.storage.postgres import db
from src.settings import DOCS_DIR


account_api = Blueprint('account', __name__)


@account_api.route('/profile/login', methods=['PATCH'])
@jwt_required()
@swag_from(DOCS_DIR.joinpath('account').joinpath('patch_login.yml'))
def patch_login():
    schema = PatchLogin()
    data = schema.flask_load(request.json)

    if User.query.filter_by(login=data['login']).first():
        return jsonify(msg='login already exists'), 409

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    user.login = data['login']
    db.session.commit()

    return jsonify(msg='updated successfully')


@account_api.route('/profile/password', methods=['PATCH'])
@jwt_required()
@swag_from(DOCS_DIR.joinpath('account').joinpath('patch_password.yml'))
def patch_password():
    schema = PatchPassword()
    data = schema.flask_load(request.json)

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user.verify_password(data['old_password']):
        return jsonify({"msg": "Bad old password"}), 409

    user.set_password(data['new_password'])
    db.session.commit()

    return jsonify(msg='updated successfully')


@account_api.route('/signin_history', methods=['GET'])
@jwt_required()
@swag_from(DOCS_DIR.joinpath('account').joinpath('signin_history.yml'))
def signin_history():
    user_id = get_jwt_identity()
    user_login_history: List[UserSignIn] = UserSignIn.query.filter_by(user_id=user_id).all()
    return jsonify([row.serialize for row in user_login_history])
