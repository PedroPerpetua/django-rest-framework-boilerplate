import django.contrib.auth.models as admin_models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from core.admin import admin_site
from extensions.admin import object_metadata_fieldset
from users import models


@admin.register(models.User, site=admin_site)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "username")
    search_fields = ("username",)
    ordering = ("created_at",)

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )

    readonly_fields = ("id", "created_at", "updated_at", "last_login")
    fieldsets = (
        (_("User details"), {"fields": ("username", "is_active", "password", "last_login")}),
        (_("Permissions"), {"fields": ("is_superuser", "is_staff", "groups", "user_permissions")}),
        object_metadata_fieldset,
    )


# Register the default Group and Permissions models.
# This next code block is a workaround to place them under the "Users" label
# See https://stackoverflow.com/questions/10561091/ for more details


class GroupProxy(admin_models.Group):
    class Meta:
        proxy = True
        verbose_name = _("group")
        verbose_name_plural = _("groups")


@admin.register(GroupProxy, site=admin_site)
class GroupAdmin(admin.ModelAdmin):
    fields = ("name", "permissions")
    filter_horizontal = ("permissions",)


class PermissionProxy(admin_models.Permission):
    class Meta:
        proxy = True
        verbose_name = _("permission")
        verbose_name_plural = _("permissions")


admin_site.register(PermissionProxy)
