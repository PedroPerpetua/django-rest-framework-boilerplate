from django.contrib.auth import get_user_model
from django.test import TestCase
from core.utilities import env


class TestMigrations(TestCase):
    """Test the migrations created manually."""

    def test_load_admin_migration(self) -> None:
        """Test that a superuser was created on migrations."""
        user_filter = get_user_model().objects.filter(is_staff=True)
        self.assertEqual(1, user_filter.count())
        user = user_filter.get()
        # Because the migrations are made BEFORE the tests, we can't actually mock them - check the originals.
        EMAIL = env.as_string("ADMIN_EMAIL")
        PASSWORD = env.as_string("ADMIN_PASSWORD")
        self.assertEqual(EMAIL, user.get_username())
        self.assertTrue(user.check_password(PASSWORD))
