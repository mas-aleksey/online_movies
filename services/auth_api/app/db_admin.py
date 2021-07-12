from flask_admin.contrib.sqla import ModelView

from app import admin, db
from app.models import User, UserSignIn, OauthUser, Role, UserRole


class UserAdminView(ModelView):
    column_hide_backrefs = False
    column_list = ('email', 'is_superuser', 'roles')


class OauthUserAdminView(ModelView):
    column_hide_backrefs = False
    column_list = ('user_id', 'social_id', 'social_name')


admin.add_view(UserAdminView(User, db.session))
admin.add_view(ModelView(UserSignIn, db.session))
admin.add_view(OauthUserAdminView(OauthUser, db.session))
admin.add_view(ModelView(Role, db.session))
admin.add_view(ModelView(UserRole, db.session))
