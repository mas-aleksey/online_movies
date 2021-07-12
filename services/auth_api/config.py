import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'postgresql://django:django@localhost:5432/ya_auth')
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379')
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ADMIN_SWATCH = 'cerulean'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'asdlkjiosdf'
    JWT_AUTH_USERNAME_KEY = 'email'
    JWT_AUTH_PASSWORD_KEY = 'password'
    JWT_AUTH_ENDPOINT = '/api/v1/login'
    JWT_BLACKLIST_ENABLED = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=1)
    YA_CLIENT_ID = os.environ.get('YA_CLIENT_ID', '0594f188c2bd4064ba257f9f6f2f2724')
    YA_CLIENT_SECRET = os.environ.get('YA_CLIENT_SECRET', 'ea2adaafd6644188a100ae0743f0dc0f')
    RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')
