from typing import Callable, Any
from wsgiref.simple_server import WSGIRequestHandler
from django.contrib import admin


class AdminSite(admin.AdminSite):
    # Define the order to show apps/models on the admin site
    ORDERING: dict[str, list[str]] = {
        # Python dicts are ordered. The first pair of the dictionary will be at the top. Fill as follows:
        # "<app_name>": ["<model1>", "<model2>", ...]
    }

    @staticmethod
    def _order_list(
        original: list[Any], ordering: list[str], func: Callable[[Any], str] = lambda x: str(x)
    ) -> list[Any]:
        retval: list[Any] = [None for _ in ordering]
        unordered: list[Any] = [] # Store the values not in ordering to append at the end
        for value in original:
            # Check if it's in the list
            try:
                index = ordering.index(func(value))
                retval[index] = value
            except ValueError:
                unordered.append(value)
        return retval + unordered

    def get_app_list(self, request: WSGIRequestHandler) -> list[Any]:
        app_dict = super()._build_app_dict(request)
        if len(app_dict) == 0:
            # No apps to display
            return []
        # Sort them according to our dict
        return self._order_list(list(app_dict.values()), list(self.ORDERING.keys()), lambda x: x['app_label'])


admin_site = AdminSite()
