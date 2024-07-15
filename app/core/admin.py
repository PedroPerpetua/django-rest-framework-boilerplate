from extensions.admin import BaseAdminSite


class AdminSite(BaseAdminSite):
    """Custom, overridable admin site."""

    ...


admin_site = AdminSite()
