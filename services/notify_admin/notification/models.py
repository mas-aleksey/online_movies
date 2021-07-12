from django.db import models
from model_utils.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _


class NotifyTemplate(TimeStampedModel):
    title = models.CharField(max_length=512, unique=True)
    short_text = models.CharField(max_length=512)
    message = models.TextField()

    class Meta:
        db_table = 'notify_template'
        verbose_name = _('шаблон нотификации')
        verbose_name_plural = _('шаблоны нотификаций')

    def __str__(self):
        return self.title
