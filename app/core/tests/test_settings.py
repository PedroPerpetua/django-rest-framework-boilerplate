from unittest import TestCase
from django.conf import settings
from rest_framework.settings import api_settings
from rest_framework.test import APIClient


class TestSettings(TestCase):
    """Testcase for a potential found issue."""

    def test_restframework_settings_loaded(self) -> None:
        """
        Test that the restframework settings loaded correctly.

        This test is here because previously we stumbled upon an issue where importing restframework BEFORE setting
        it's settings on the `settings.py` file would result on these settings never being loaded. It's easy to have
        an import nested deep into other imports and miss that this is happening, resulting in a hidden bug. This test
        makes sure the settings are being imported correctly.

        If this test fails, make sure to check the imports in your new code. This usually happens because you imported
        a type from `core.utilities.types` at runtime, resulting in restframework being imported too and screwing it
        up. This can be fixed by importing the type with an `if TYPE_CHECKING` block.
        """
        self.assertEqual(settings.REST_FRAMEWORK, api_settings.user_settings)

    def test_restframework_defaults_json(self) -> None:
        """Test that restframework's test client defaults to json."""
        client = APIClient()
        # Nesting the `data` key fails with the default "multipart" format.
        req = client.post("", data={"data": {"nested": "_data"}})
        self.assertEqual("application/json", req.request["CONTENT_TYPE"])
