from typing import Any, Callable, Optional, TypeVar
from django.contrib import admin
from django.http import HttpRequest


# Typevar for our _order_list method
T = TypeVar("T")


class AdminSite(admin.AdminSite):
    # Define the order to show apps/models on the admin site
    ORDERING: dict[str, list[str]] = {
        # Python dicts are ordered. The first pair of the dictionary will be at the top. Fill as follows:
        # "<app_name>": ["<model1>", "<model2>", ...]
        # NOTE: apps and models are case sensitive
        "users": []  # Default ordering is fine
    }

    @staticmethod
    def _order_list(original: list[T], ordering: list[str], func: Callable[[T], str] = lambda x: str(x)) -> list[T]:
        retval: list[T | None] = [None for _ in ordering]
        unordered: list[T] = []  # Store the values not in ordering to append at the end
        for value in original:
            # Check if it's in the list
            try:
                index = ordering.index(func(value))
                retval[index] = value
            except ValueError:
                unordered.append(value)
        return [v for v in retval if v is not None] + unordered

    def get_app_list(self, request: HttpRequest, app_label: Optional[str] = None) -> list[Any]:
        app_dict = super()._build_app_dict(request)
        if len(app_dict) == 0:
            # No apps to display
            return []
        # Order the apps first
        ordered_apps = self._order_list(
            list(app_dict.values()), list(self.ORDERING.keys()), lambda x: str(x["app_label"])
        )
        # Then order the Models inside the apps
        for app in ordered_apps:
            label = app["app_label"]
            if label in self.ORDERING and len(self.ORDERING[label]) > 0:
                app["models"] = self._order_list(list(app["models"]), self.ORDERING[label], lambda x: str(x["name"]))
        return ordered_apps


admin_site = AdminSite()
