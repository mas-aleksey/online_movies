from uuid import uuid4

from django.conf import settings

from billing.apps.subscriptions.models import (
    Client, AuditEvents, AccessType
)
from billing.services.auth import delete_auth_user_role, add_auth_user_role


def get_or_create_client(user_id: str) -> Client:
    client = Client.objects.filter(user_id=user_id).first()
    if not client:
        client = Client(id=uuid4(), user_id=user_id)
        client.save()
        AuditEvents.create('system', 'create', client)
    return client


def set_auth_client_roles(client_id: str):
    """Устанавливает роли пользователя на основе действующих подписок."""

    client = Client.objects.get(id=client_id)

    # получаем уровни доступа
    all_types = set(AccessType.values)
    user_types = client.get_current_access_types()

    # получаем роли
    all_roles = set(role for x in all_types for role in settings.ACCESS_ROLES_MAPPING[x])
    user_roles = set(role for x in user_types for role in settings.ACCESS_ROLES_MAPPING[x])
    delete_roles = all_roles - user_roles

    # удаляем не нужные роли
    delete_auth_user_role(client.user_id, list(delete_roles))
    AuditEvents.create('system', f'deleted: {delete_roles}', client)

    # добавляем нужные
    add_auth_user_role(client.user_id, list(user_roles))
    AuditEvents.create('system', f'granted: {user_roles}', client)

    client.roles_updated = True
    client.save(update_fields=['roles_updated'])
