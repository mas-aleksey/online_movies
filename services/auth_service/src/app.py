from flask import Flask
from src.api.v1 import auth_api, account_api, roles_api, users_api
from src.storage.postgres import init_db
from src.app_extensions import init_jwt, init_oauth, init_swagger


app = Flask(__name__)

app.register_blueprint(auth_api, url_prefix='/auth2/api/v1/auth')
app.register_blueprint(account_api, url_prefix='/auth2/api/v1/account')
app.register_blueprint(roles_api, url_prefix='/auth2/api/v1/roles')
app.register_blueprint(users_api, url_prefix='/auth2/api/v1/users')


def init_app():
    init_db(app)
    init_jwt(app)
    init_swagger(app)
    init_oauth(app)


if __name__ == '__main__':
    init_app()
    app.run()
