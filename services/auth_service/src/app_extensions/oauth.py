from flask import Flask
from authlib.integrations.flask_client import OAuth
from src.settings import OAUTH, SECRET_KEY, RECAPTCHA_PUBLIC_KEY

oauth = OAuth()


def init_oauth(app: Flask):
    app.config["SECRET_KEY"] = SECRET_KEY
    oauth.init_app(app)
    oauth.register(**OAUTH['Google'])

    app.config['RECAPTCHA_PUBLIC_KEY'] = RECAPTCHA_PUBLIC_KEY
    app.config['TESTING'] = True
