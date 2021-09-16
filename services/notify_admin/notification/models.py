from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Notify(TimeStampedModel):
    name = models.CharField(_('нотификация'), max_length=512, unique=True)
    code = models.CharField(_('код'), max_length=512, unique=True)

    class Meta:
        verbose_name = _('нотификации')
        verbose_name_plural = _('нотификация')

    def __str__(self):
        return str(self.name)


class NotifyTemplate(TimeStampedModel):
    title = models.CharField(max_length=512, unique=True)
    notify = models.OneToOneField(Notify, verbose_name=_('нотификация'),
                                  on_delete=models.CASCADE, null=True, default=None, unique=True)
    short_text = models.CharField(max_length=512)
    message = models.TextField()

    def save(self, *args, **kwargs):
        if self.notify:
            self.title = self.notify.code
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'notify_template'
        verbose_name = _('шаблон нотификации')
        verbose_name_plural = _('шаблоны нотификаций')

    def __str__(self):
        return str(self.notify)


class Channel(TimeStampedModel):
    name = models.CharField(_('канал'), max_length=512, unique=True)
    code = models.CharField(_('код'), max_length=512, unique=True)

    class Meta:
        verbose_name = _('канал нотификации')
        verbose_name_plural = _('каналы нотификаций')

    def __str__(self):
        return str(self.name)


class Client(TimeStampedModel):
    id = models.UUIDField(primary_key=True)
    user_id = models.UUIDField(_('uuid пользователя'), unique=True)

    class Meta:
        verbose_name = _('клиент')
        verbose_name_plural = _('клиенты')

    def __str__(self):
        return str(self.user_id)


class AllowChannel(TimeStampedModel):
    channel = models.ForeignKey(Channel, verbose_name=_('канал'), on_delete=models.CASCADE)
    notify = models.ForeignKey(Notify, verbose_name=_('нотификация'), on_delete=models.CASCADE)
    client = models.ForeignKey(Client, verbose_name=_('пользователь'), on_delete=models.CASCADE)
    enabled = models.BooleanField(_('Включен'), default=True)

    class Meta:
        verbose_name = _('канал пользователя')
        verbose_name_plural = _('каналы пользователя')
        unique_together = ('channel', 'notify', 'client')

    def __str__(self):
        return f'{self.channel}:{self.client}'
