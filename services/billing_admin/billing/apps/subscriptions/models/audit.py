import logging

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

from billing.apps.subscriptions.tasks import audit_create_task

logger = logging.getLogger(__name__)


class AuditMixin(models.Model):
    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, action=None):
        super().save(force_insert, force_update, using, update_fields)
        status = action or getattr(self, 'status', 'something')
        AuditEvents.create('models', status, self, self.details)

    @property
    def details(self) -> str:
        return str(model_to_dict(self))


class AuditEvents(TimeStampedModel):
    """История событий."""
    who = models.CharField(_("Инициатор события"), max_length=50)
    what = models.CharField(_("Событие"), max_length=50)
    details = models.TextField(_("Подробности"), blank=True, null=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, default=None, null=True, blank=True)
    object_id = models.CharField(max_length=100, default=None, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('событие')
        verbose_name_plural = _('события')

    @classmethod
    def create(cls, who, what, instance, details=None) -> None:
        audit_create_task.apply_async(
            args=(who, what, instance._meta.app_label, instance._meta.object_name, instance.id, details)
        )
