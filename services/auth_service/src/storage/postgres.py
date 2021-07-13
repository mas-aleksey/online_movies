from flask import Flask
from sqlalchemy.engine.url import URL
from flask_sqlalchemy import SQLAlchemy
from src.settings import DATABASE, FIRST_START, ROLES, SUPER_USER

db = SQLAlchemy()


def init_fill_db(app):
    db.app = app
    db.create_all()

    from src.models.db_models import Role, User
    for role in ROLES:
        if not Role.get_by_name(role):
            db.session.add(Role(role))

    user = User.query.filter_by(email=SUPER_USER['email']).first()
    if not user:
        user = User(SUPER_USER['email'])
        user.set_password(SUPER_USER['password'])
        db.session.add(user)
    user.superuser = True
    db.session.commit()


def init_db(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = URL.create(**DATABASE)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.init_app(app)

    if FIRST_START:
        init_fill_db(app)
