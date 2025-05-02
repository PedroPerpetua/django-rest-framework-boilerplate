from django.urls import include, path
from core import views
from core.admin import admin_site
from extensions.utilities.types import URLPatternsList


# This line is commented due to a possible issue with django that breaks the urls
# See: https://forum.djangoproject.com/t/custom-adminsite-clashes-with-app-name-throws-noreversematch-at-admin/18380
# app_name = "core"

urlpatterns: URLPatternsList = [
    path("admin/", admin_site.urls, name="admin"),
    path(
        "schema/",
        include(
            [
                path("", views.SpectacularAPIView.as_view(), name="schema"),
                path("swagger/", views.SpectacularSwaggerView.as_view(), name="schema-swagger"),
            ]
        ),
    ),
    path("ping/", views.PingView.as_view(), name="ping"),
]
