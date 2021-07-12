from flask import request, jsonify, redirect
from flask_jwt_extended import (jwt_required, get_jwt_identity, get_jwt)
from flask_restful import Resource, abort
from marshmallow import ValidationError

from app import db
from app.decorators import is_superuser
from app.models import User, UserSignIn, OauthUser, Role, UserRole
from app.schemas import UserSchema, UserSignInSchema, ChangePasswordSchema, UserCRUDSchema, RoleSchema, UserRoleSchema
from app.service import create_tokens, refresh_tokens, get_user_by_credentials, user_logout_by_device, \
    get_or_create_oauth_user, OAuthService
from utils.recaptcha import recaptcha_check


class BaseRUDApiView(Resource):
    """Базовый класс для редактирования модели."""
    schema = None
    model = None

    @jwt_required()
    @is_superuser
    def dispatch_request(self, *args, **kwargs):
        return super().dispatch_request(*args, **kwargs)

    def get(self, pk, *args, **kwargs):
        """Просмотр записи"""
        instance = self.model.query.get_or_404(pk)
        schema = self.schema()
        return schema.dump(instance), 200

    def put(self, pk, *args, **kwargs):
        """Обновление запси"""
        instance = self.model.query.get_or_404(pk)
        schema = self.schema(partial=True)

        try:
            data = schema.load(request.json)
        except ValidationError as err:
            raise abort(400, message=err.messages)

        self.model.query.filter_by(id=pk).update(data)
        db.session.commit()

        return schema.dump(instance), 200

    def delete(self, pk, *args, **kwargs):
        """Удаление записи"""
        self.model.query.filter_by(id=pk).delete()
        db.session.commit()
        return jsonify(msg="deleted")


class BaseListCreateApiView(Resource):
    """Базовый класс создания и просмотра списка объектов модели."""
    schema = None
    model = None

    @jwt_required()
    @is_superuser
    def dispatch_request(self, *args, **kwargs):
        return super().dispatch_request(*args, **kwargs)

    def get_query(self, *args, **kwargs):
        return self.model.query

    def get(self, *args, **kwargs):
        """Список записей"""
        print(2)
        schema = self.schema(many=True)
        results = self.get_query(*args, **kwargs).all()
        return schema.dump(results), 200

    def post(self, *args, **kwargs):
        """Создание записи"""
        schema = self.schema(partial=False)

        try:
            data = schema.load(request.json)
        except ValidationError as err:
            raise abort(400, message=err.messages)

        instance = self.model(**data)
        db.session.add(instance)
        db.session.commit()

        return schema.dump(instance)


class RegistrationApiView(Resource):
    """Представление для регистрации пользователя."""

    def post(self):
        data = request.json
        token = data.pop('recaptcha')
        recaptcha_check(request, token)

        schema = UserCRUDSchema()
        try:
            user = schema.load(data)
        except ValidationError as err:
            raise abort(400, message=err.messages)

        db.session.add(user)
        db.session.commit()
        return schema.dump(user)


class LoginApiView(Resource):
    """Представление для авторизации пользователя."""

    def post(self):
        data = request.json
        token = data.pop('recaptcha')
        recaptcha_check(request, token)

        schema = UserSchema()
        try:
            data = schema.load(data)
        except ValidationError as err:
            raise abort(400, message=err.messages)

        user = get_user_by_credentials(data.email, data.password)
        if not user:
            raise abort(400, message={'email': 'Неверное имя пользователя или пароль.'})

        device = request.headers['User-Agent']

        tokens = create_tokens(user, device)
        return jsonify(tokens)


class ChangePasswordApiView(Resource):
    """Представление для смены пароля."""

    @jwt_required()
    def post(self):
        schema = ChangePasswordSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            raise abort(400, message=err.messages)

        current_user = get_jwt_identity()
        user = get_user_by_credentials(current_user, data['password'])
        if not user:
            raise abort(400, message={'email': 'Неверное имя пользователя или пароль.'})

        user.password = user.generate_hash(data['new_password'])
        db.session.commit()
        return jsonify(msg='success')


class TokenRefreshApiView(Resource):
    """Представление для обновления токенов."""

    @jwt_required(refresh=True)
    def post(self):
        tokens = refresh_tokens(get_jwt())
        return jsonify(tokens)


class LogoutApiView(Resource):
    """Представление для выхода из системы."""

    @jwt_required()
    def get(self):
        email = get_jwt()['sub']
        device = get_jwt()['device']
        user = User.query.filter_by(email=email).first()
        user_logout_by_device(user, device)
        return jsonify(msg="Access token revoked")


class UserSignInApiView(Resource):
    """Представление для просмотра историй входа."""

    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()
        signs = UserSignIn.query.filter_by(user_id=user.id).all()
        schema = UserSignInSchema(many=True)
        return schema.dump(signs)


class SocialAuthApiView(Resource):
    """Представление для входа через соцсети."""

    def __init__(self, **kwargs):
        self.view = getattr(self, kwargs['view'])

    def login(self, backend: str):
        oauth_service = OAuthService(backend)
        url = oauth_service.get_login_url()
        return redirect(url, 302)

    def callback(self, backend: str):
        oauth_service = OAuthService(backend)
        oauth_user = oauth_service.callback(request)
        user = get_or_create_oauth_user(oauth_user)
        device = request.headers['User-Agent']
        tokens = create_tokens(user, device)
        return jsonify(tokens)

    def get(self, *args, **kwargs):
        return self.view(*args, **kwargs)


class VerifyTokenApiView(Resource):
    """Представление для проверки актуальности токена."""

    @jwt_required()
    def get(self):
        return True


class UserListCreateApiView(BaseListCreateApiView):
    """Просмотр и создание пользователей"""
    schema = UserCRUDSchema
    model = User


class UserRUDApiView(BaseRUDApiView):
    """RUD представление для пользователя"""
    schema = UserCRUDSchema
    model = User

    def delete(self, pk, *args, **kwargs):
        """Удаление пользователя"""
        OauthUser.query.filter_by(user_id=pk).delete()
        UserSignIn.query.filter_by(user_id=pk).delete()
        User.query.filter_by(id=pk).delete()
        db.session.commit()
        return jsonify(msg="deleted")


class RoleListCreateApiView(BaseListCreateApiView):
    """Просмотр и создание ролей."""
    schema = RoleSchema
    model = Role


class RoleRUDApiView(BaseRUDApiView):
    """RUD представление для роли"""
    schema = RoleSchema
    model = Role

    def delete(self, pk, *args, **kwargs):
        """Удаление роли"""
        UserRole.query.filter_by(role_id=pk).delete()
        Role.query.filter_by(id=pk).delete()
        db.session.commit()
        return jsonify(msg="deleted")


class UserRoleListCreateApiView(BaseListCreateApiView):
    """Просмотр и добавление ролей пользователя."""
    schema = UserRoleSchema
    model = UserRole

    def get_query(self, *args, **kwargs):
        query = super().get_query(*args, **kwargs)
        query = query.filter_by(user_id=kwargs.get('pk'))
        return query


class UserRoleRUDApiView(BaseRUDApiView):
    """RUD представление для роли пользователя"""
    schema = UserRoleSchema
    model = UserRole
