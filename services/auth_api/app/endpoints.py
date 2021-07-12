from app import api, views

base_url = '/v1'

api.add_resource(views.UserListCreateApiView, f'{base_url}/admin/users')
api.add_resource(views.UserRUDApiView, f'{base_url}/admin/users/<pk>')
api.add_resource(views.UserRoleListCreateApiView, f'{base_url}/admin/users/<pk>/roles')
api.add_resource(views.UserRoleRUDApiView, f'{base_url}/admin/user_roles/<pk>')
api.add_resource(views.RoleListCreateApiView, f'{base_url}/admin/roles')
api.add_resource(views.RoleRUDApiView, f'{base_url}/admin/roles/<pk>')
api.add_resource(views.RegistrationApiView, f'{base_url}/user/registration')
api.add_resource(views.ChangePasswordApiView, f'{base_url}/user/password')
api.add_resource(views.LoginApiView, f'{base_url}/login')
api.add_resource(views.LogoutApiView, f'{base_url}/logout')
api.add_resource(views.TokenRefreshApiView, f'{base_url}/token/refresh')
api.add_resource(views.VerifyTokenApiView, f'{base_url}/token/verify')
api.add_resource(views.UserSignInApiView, f'{base_url}/user/journal/login')

api.add_resource(
    views.SocialAuthApiView,
    f'{base_url}/social_auth/login/<backend>',
    resource_class_kwargs={'view': 'login'},
    endpoint="social_auth_login"
)

api.add_resource(
    views.SocialAuthApiView,
    f'{base_url}/social_auth/callback/<backend>',
    resource_class_kwargs={'view': 'callback'},
    endpoint="social_auth_callback"
)
