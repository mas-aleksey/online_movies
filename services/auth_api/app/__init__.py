from flask import Flask
from flask_admin import Admin
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_redis import FlaskRedis
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)

db = SQLAlchemy()
migrate = Migrate()
redis_db = FlaskRedis()
admin = Admin(name='auth_api', url='/auth/admin', template_mode='bootstrap3')
api = Api(prefix='/auth/api')
ma = Marshmallow()
jwt = JWTManager()


def create_app(config_class=Config):
    app.config.from_object(config_class)
    db.init_app(app)
    redis_db.init_app(app)
    migrate.init_app(app, db, directory='migrations')
    admin.init_app(app)
    api.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    return app


from . import models, db_admin, endpoints  # noqa
