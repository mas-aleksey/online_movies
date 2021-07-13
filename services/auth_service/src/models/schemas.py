from flask import abort, jsonify, make_response
from marshmallow.validate import Length, ValidationError, Regexp
from marshmallow import fields, Schema


class BaseSchema(Schema):

    def flask_load(self, data):
        try:
            return self.load(data)
        except ValidationError as exc:
            abort(make_response(jsonify(errors=exc.messages), 400))


class LoginSchema(BaseSchema):
    email = fields.String(required=True)
    password = fields.String(required=True)


class SignInSchema(LoginSchema):
    email = fields.String(required=True, validate=[
        Regexp(
            '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$',
            error='Email is invalid'
        ),
        Length(min=4)
    ])
    password = fields.String(required=True, validate=Length(min=6))


class PatchLogin(BaseSchema):
    login = fields.String(required=True)


class PatchPassword(BaseSchema):
    old_password = fields.String(required=True)
    new_password = fields.String(required=True, validate=Length(min=6))


class RoleSchema(BaseSchema):
    role = fields.String(required=True)


class RolePathSchema(BaseSchema):
    old_role = fields.String(required=True)
    new_role = fields.String(required=True)