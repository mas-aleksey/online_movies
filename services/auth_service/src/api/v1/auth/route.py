import uuid
from flask import Blueprint, request, jsonify, url_for, render_template
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, set_refresh_cookies, set_access_cookies

from src.models.db_models import User, UserSignIn, SocialAccount
from src.models.schemas import LoginSchema, SignInSchema
from src.app_extensions.jwt_tokens import genetare_tokens
from src.app_extensions.oauth import oauth
from src.storage.postgres import db
from src.storage.redis import delete_user_tokens, revoke_token
from src.settings import ACCESS_EXPIRES, REFRESH_EXPIRES, DOCS_DIR, DEFAULT_ROLE, TEMPLATE_DIR
from src.api.v1.auth.forms import RecaptchaForm


auth_api = Blueprint('auth', __name__, template_folder=TEMPLATE_DIR)


def signin_audit(user_id: str, user_agent: str) -> None:
    device_type = 'mobile' if 'mobile' in user_agent.lower() else 'web'
    signin = UserSignIn(user_id=user_id, user_agent=user_agent, user_device_type=device_type)
    db.session.add(signin)
    db.session.commit()


def create_new_user(email: str, password: str) -> User:
    user = User(email, DEFAULT_ROLE)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def oauth_login(social_name: str, social_id, user_email: str, user_agent) -> dict:
    user = User.query.filter_by(email=user_email).first()
    if not user:
        user = create_new_user(user_email, str(uuid.uuid4()))
    user_id = str(user.id)

    s_account = SocialAccount.query.filter_by(user_id=user_id, social_id=social_id, social_name=social_name).first()
    if not s_account:
        acc = SocialAccount(user_id=user_id, social_id=social_id, social_name=social_name)
        db.session.add(acc)
        db.session.commit()

    signin_audit(user_id, user_agent)

    access_token, refresh_token = genetare_tokens(user=user, user_agent=user_agent)
    return jsonify(access_token=access_token, refresh_token=refresh_token)


@auth_api.route('/captcha', methods=['GET', 'POST'])
def captcha():
    form = RecaptchaForm()
    if not form.validate_on_submit():
        return render_template('captcha.html', form=form)

    if request.method == 'POST':
        return 'Submitted!'


@auth_api.route('/login', methods=['POST'])
@swag_from(DOCS_DIR.joinpath('auth').joinpath('login.yml'))
def login():
    schema = LoginSchema()
    data = schema.flask_load(request.json)
    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.verify_password(data['password']):
        return jsonify({"msg": "Bad email or password"}), 409

    signin_audit(str(user.id), request.user_agent.string)

    access_token, refresh_token = genetare_tokens(user=user, user_agent=request.user_agent.string)
    return jsonify(access_token=access_token, refresh_token=refresh_token)


@auth_api.route('/google-login', methods=['GET'])
@swag_from(DOCS_DIR.joinpath('auth').joinpath('google-login.yml'))
def google_login():
    redirect_uri = url_for('auth.google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_api.route('/google-auth', methods=['GET'])
@swag_from(DOCS_DIR.joinpath('auth').joinpath('google-auth.yml'))
def google_auth():
    oauth_token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(oauth_token)
    social_id = user.get('sub')
    user_email = user.get('email')

    return oauth_login('google', social_id, user_email, request.user_agent.string)


@auth_api.route('/signup', methods=['POST'])
@swag_from(DOCS_DIR.joinpath('auth').joinpath('signup.yml'))
def signup():
    schema = SignInSchema()
    data = schema.flask_load(request.json)

    if User.query.filter_by(email=data['email']).first():
        return jsonify(msg='email already exists'), 409

    create_new_user(data['email'], data['password'])
    return jsonify(msg='registered successfully')


@auth_api.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@swag_from(DOCS_DIR.joinpath('auth').joinpath('refresh.yml'))
def refresh():
    refresh_jti = get_jwt()["jti"]
    revoke_token(refresh_jti, refresh=True)

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify(msg='user does not exist'), 409

    access_token, refresh_token = genetare_tokens(user=user, user_agent=request.user_agent.string)
    return jsonify(access_token=access_token, refresh_token=refresh_token)


@auth_api.route('/logout', methods=['DELETE'])
@jwt_required()
@swag_from(DOCS_DIR.joinpath('auth').joinpath('logout.yml'))
def logout():
    access_jti = get_jwt()["jti"]
    revoke_token(access_jti)
    return jsonify(msg="Access token revoked")


@auth_api.route('/logout_all_accounts', methods=['DELETE'])
@jwt_required()
@swag_from(DOCS_DIR.joinpath('auth').joinpath('logout_all_accounts.yml'))
def logout_all_accounts():
    user_id = get_jwt_identity()
    delete_user_tokens(user_id)
    return jsonify(msg="all user tokens are revoked")


@auth_api.route('/access_check', methods=['GET'])
@jwt_required()
@swag_from(DOCS_DIR.joinpath('auth').joinpath('access_check.yml'))
def access_check():
    user_roles = get_jwt()["roles"]
    is_super = get_jwt()["superuser"]
    user_id = get_jwt()["sub"]
    return jsonify(is_super=is_super, roles=user_roles, user_id=user_id)
