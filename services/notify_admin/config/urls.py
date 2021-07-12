from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('notify/admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar  # type: ignore # noqa
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # noqa

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += staticfiles_urlpatterns()  # type: ignore
