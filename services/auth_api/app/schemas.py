from marshmallow import fields, post_load, EXCLUDE, ValidationError, pre_load

from app import ma
from .models import User, UserSignIn, Role, UserRole


def user_email_unique_validator(email):
    user_exists = User.query.filter_by(email=email).first()

    if user_exists:
        raise ValidationError({'email': "Такой email уже зарегистрирован."})


class UserSchema(ma.SQLAlchemySchema):
    """Схема для регистрации пользователя."""

    email = fields.Email()
    password = fields.Str(load_only=True)

    class Meta:
        model = User
        load_instance = True
        fields = ("email", "password")


class ChangePasswordSchema(ma.Schema):
    """Схема для токенов."""

    password = fields.String(required=True)
    new_password = fields.String(required=True)

    class Meta:
        fields = ("password", "new_password")


class UserSignInSchema(ma.SQLAlchemySchema):
    """Схема для для просмотра историй входа."""

    class Meta:
        model = UserSignIn
        fields = ("logined_by", "user_agent")


class UserCRUDSchema(ma.SQLAlchemyAutoSchema):
    @pre_load
    def validate(self, item, **kwargs):
        if 'email' in item:
            user_email_unique_validator(item['email'])
        return item

    @post_load
    def full_clean(self, item, **kwargs):
        if 'password' in item:
            item['password'] = User.generate_hash(item['password'])
        if 'email' in item:
            item['email'] = item['email'].lower().strip()
        return item

    class Meta:
        model = User
        unknown = EXCLUDE
        partial = True
        load_instance = True
        load_only = ['password']


class RoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        unknown = EXCLUDE
        partial = True


class UserRoleSchema(ma.SQLAlchemyAutoSchema):
    role = ma.Nested(RoleSchema, dump_only=True)

    class Meta:
        model = UserRole
        fields = ['role_id', 'user_id', 'role']
        load_only = ['role_id', 'user_id']
