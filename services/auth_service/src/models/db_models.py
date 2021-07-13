import uuid
import datetime
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash
from src.storage.postgres import db


def create_partition(target, connection, **kw) -> None:
    """ creating partition by user_sign_in """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_smart" PARTITION OF "users_sign_in" FOR VALUES IN ('smart')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_mobile" PARTITION OF "users_sign_in" FOR VALUES IN ('mobile')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_web" PARTITION OF "users_sign_in" FOR VALUES IN ('web')"""
    )


users_roles = db.Table(
    'users_roles',
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('users.id')),
    db.Column('role_id', UUID(as_uuid=True), db.ForeignKey('roles.id'))
)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    username = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    superuser = db.Column(db.Boolean, default=False)
    roles = db.relationship(
        'Role',
        secondary=users_roles,
        backref=db.backref('members', lazy='dynamic')
    )

    def __init__(self, email, role_name=None):
        self.email = email
        if role_name:
            role = Role.get_by_name(role_name)
            if role:
                self.roles.append(role)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')

    def __repr__(self):
        return f'<User {self.email}>'


class UserSignIn(db.Model):
    __tablename__ = 'users_sign_in'
    __table_args__ = {
        'postgresql_partition_by': 'LIST (user_device_type)',
        'listeners': [('after_create', create_partition)],
    }

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    logined_by = db.Column(db.DateTime, default=datetime.datetime.utcnow, primary_key=True)
    user_agent = db.Column(db.Text, primary_key=True)
    user_device_type = db.Column(db.Text, primary_key=True)

    def __repr__(self):
        return f'<UserSignIn {self.user_id}:{self.logined_by}>'

    @property
    def serialize(self):
        return {
            'logined_by': self.logined_by,
            'user_agent': self.user_agent,
            'user_device_type': self.user_device_type
        }


class SocialAccount(db.Model):
    __tablename__ = 'social_account'
    __table_args__ = (
        db.UniqueConstraint('social_id', 'social_name', name='social_pk'),
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship(User, backref=db.backref('social_accounts', lazy=True))

    social_id = db.Column(db.Text, nullable=False)
    social_name = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Role {self.name}>'

    @staticmethod
    def get_by_name(name):
        return Role.query.filter_by(name=name).first()
