from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional
from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from extensions.utilities import order_list


if TYPE_CHECKING:
    from django.contrib.admin.options import _FieldOpts
    from django.utils.functional import _StrOrPromise


class BaseAdminSite(admin.AdminSite):
    """
    Custom admin site base with an extension that allows the apps to be sorted, as well as the models within them.

    See the documentation on `ORDERING` to know how to order models and apps.
    """
    # For a REST server, the site url will usually be a different domain, and we can't link that here.
    site_url = None

    ORDERING: dict[str, list[str]] = {}
    """
    Define the order to show apps/models on the admin site.

    Python dicts are ordered. The first pair of the dictionary will be at the top. Fill as follows:
    "<app_name>": ["<model1>", "<model2>", ...]

    NOTE: apps and models are case sensitive
    """

    def get_app_list(self, request: HttpRequest, app_label: Optional[str] = None) -> list[Any]:  # pragma: no cover
        """Override this method so we can order them according ot our own ordering."""
        app_dict = super()._build_app_dict(request)
        if len(app_dict) == 0:
            # No apps to display
            return []
        # Order the apps first
        ordered_apps = order_list(list(app_dict.values()), list(self.ORDERING.keys()), lambda x: str(x["app_label"]))
        # Then order the Models inside the apps
        for app in ordered_apps:
            label = app["app_label"]
            if label in self.ORDERING and len(self.ORDERING[label]) > 0:
                app["models"] = order_list(list(app["models"]), self.ORDERING[label], lambda x: str(x["name"]))
        return ordered_apps


object_metadata_fieldset: tuple[_StrOrPromise | None, _FieldOpts] = (
    _("Object metadata"),
    {"fields": ("id", "is_deleted", "created_at", "updated_at")},
)
"""
Standard Object Metadata fieldset that includes the fields `id`, `is_deleted`, `created_at` and `updated_at`.

To use, just include it in the fieldsets' tuple of a Model Admin.
"""
