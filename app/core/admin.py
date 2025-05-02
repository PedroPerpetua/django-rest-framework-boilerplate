from constance.admin import Config, ConstanceAdmin  # type: ignore[import-untyped]
from extensions.admin import BaseAdminSite


class AdminSite(BaseAdminSite):
    """Custom, overridable admin site."""

    ...


admin_site = AdminSite()

# Register the Constance configs
admin_site.register([Config], ConstanceAdmin)
