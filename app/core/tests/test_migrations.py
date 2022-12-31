import os
from django.contrib.auth import get_user_model
from django.test import TestCase


class TestMigrations(TestCase):
    """Test the migrations created manually."""

    def test_load_admin_migration(self) -> None:
        """Test that a superuser was created on migrations."""
        from django.contrib.auth.models import User
        if get_user_model() != User:
            # Safe guard. If the default user model has been overridden, this test should be adjusted.
            self.fail(
                "Current user model is different from the Django default user model. This test should be adjusted!"
            )
        user_filter = User.objects.filter(is_superuser=True)
        self.assertEqual(1, user_filter.count())
        user = user_filter.get()
        # Because the migrations are made BEFORE the tests, we can't actually mock them - check the originals.
        ENV = os.environ
        USERNAME = ENV["ADMIN_USERNAME"]
        EMAIL = ENV["ADMIN_EMAIL"]
        PASSWORD = ENV["ADMIN_PASSWORD"]
        self.assertEqual(USERNAME, user.get_username())
        self.assertEqual(EMAIL, user.email)
        self.assertTrue(user.check_password(PASSWORD))
