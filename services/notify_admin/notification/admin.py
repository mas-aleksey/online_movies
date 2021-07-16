from django.contrib import admin
from .models import NotifyTemplate, Channel, AllowChannel, Client, Notify


@admin.register(NotifyTemplate)
class EmailNotificationAdmin(admin.ModelAdmin):
    exclude = ['title']


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    pass


class AllowChannelInlineAdmin(admin.TabularInline):
    model = AllowChannel


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    inlines = [AllowChannelInlineAdmin]


@admin.register(Notify)
class NotifyAdmin(admin.ModelAdmin):
    pass
