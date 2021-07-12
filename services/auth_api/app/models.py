import datetime
import uuid

from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy.dialects.postgresql import UUID

from app import db


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'{self.name}'


class User(db.Model):
    """Модель пользователя."""

    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    is_superuser = db.Column(db.Boolean, default=False)

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    def verify_password(self, password):
        return self.verify_hash(password, self.password)

    def password_to_hash(self):
        self.password = self.generate_hash(self.password)

    def __repr__(self):
        return f'<User {self.email}>'


class UserRole(db.Model):
    __tablename__ = "users_roles"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))
    user = db.relationship("User", backref="roles")
    role = db.relationship("Role", backref="users")

    def __repr__(self):
        return f'<user_id {self.user_id}  role_id {self.role_id}>'


class UserSignIn(db.Model):
    """Модель для сохранения истории входа."""

    __tablename__ = 'users_sign_in'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    logined_by = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_agent = db.Column(db.Text)
    user_device_type = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<UserSignIn {self.user_id}:{self.logined_by}>'


class OauthUser(db.Model):
    """Модель для хранения данных пользователя из соцсетей"""

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    social_id = db.Column(db.Text)
    social_name = db.Column(db.Text)

    def __repr__(self):
        return f'<YaUser {self.user_id}:{self.social_id}>'
