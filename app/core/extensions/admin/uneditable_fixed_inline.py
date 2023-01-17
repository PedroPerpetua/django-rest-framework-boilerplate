from typing import Any
from django.contrib import admin


class UneditableFixedInline(admin.TabularInline):
    """
    Modified version of Django's TabularInline with two characteristics:
    - The user never had permission to add, change or delete;
    - Uses the "fixed" template where the object name is removed.
    """

    template = "admin/fixed_tabular_inline.html"

    def has_add_permission(self, *args: Any, **kwargs: Any) -> bool:
        return False

    def has_change_permission(self, *args: Any, **kwargs: Any) -> bool:
        return False

    def has_delete_permission(self, *args: Any, **kwargs: Any) -> bool:
        return False
