from django.urls import path
from core.admin import admin_site
from core.utilities.types import URLPatternsList
from core.views import PingView


# This line is commented due to a possible issue with django that breaks the urls
# See: https://forum.djangoproject.com/t/custom-adminsite-clashes-with-app-name-throws-noreversematch-at-admin/18380
# app_name = "core"

urlpatterns: URLPatternsList = [
    path("admin/", admin_site.urls, name="admin"),
    path("ping/", PingView.as_view(), name="ping"),
]
