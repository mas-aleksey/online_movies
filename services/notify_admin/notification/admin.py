from django.contrib import admin
from .models import NotifyTemplate


@admin.register(NotifyTemplate)
class EmailNotificationAdmin(admin.ModelAdmin):
    pass