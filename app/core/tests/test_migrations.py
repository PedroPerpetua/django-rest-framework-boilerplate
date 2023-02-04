from unittest.mock import ANY
from django.contrib.auth import get_user_model
from django.test import TestCase
from core.utilities import env


class TestMigrations(TestCase):
    """Test the migrations created manually."""

    def test_load_admin_migration(self) -> None:
        """Test that a superuser was created on migrations."""
        user_filter = get_user_model().objects.filter(is_staff=True, is_superuser=True)
        self.assertEqual(1, user_filter.count())
        user = user_filter.get()
        # Because the migrations are made BEFORE the tests, we can't actually mock them - check the originals.
        credentials = env.as_json("ADMIN_CREDENTIALS")
        if not isinstance(credentials, dict):
            self.fail(f"Environment credentials are not a JSON Object: {credentials}")
        for key, value in credentials.items():
            if key == "password":
                self.assertTrue(user.check_password(value))
                continue
            # We use default match `ANY` because we can pass fields that don't exist from the configuration
            self.assertEqual(value, getattr(user, key, ANY))
