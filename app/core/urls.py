from django.urls import path
from core.admin import admin_site
from core.views import PingView


urlpatterns = [
    path("admin/", admin_site.urls, name="admin"),
    path("ping/", PingView.as_view(), name="ping"),
]
