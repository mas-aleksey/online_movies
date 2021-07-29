from uuid import uuid4

from billing.apps.subscriptions.models import (
    Client, AuditEvents
)


def get_or_create_client(user_id: str) -> Client:
    client = Client.objects.filter(user_id=user_id).first()
    if not client:
        client = Client(id=uuid4(), user_id=user_id)
        client.save()
        AuditEvents.create('system', 'create', client)
    return client
