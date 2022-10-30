from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model


class TestMigrations(TestCase):
    """Test the migrations created manually."""

    def test_load_admin_migration(self):
        """Test that a superuser was created on migrations."""
        from django.contrib.auth.models import User
        if get_user_model() != User:
            # Safe guard. If the default user model has been overridden, this
            # test should be adjusted and this check removed.
            self.fail(
                "Current user model is different from the Django default "
                "user model. This test should be adjusted!"
            )
        user_filter = User.objects.filter(is_superuser=True)
        self.assertEqual(1, user_filter.count())
        user = user_filter.get()
        # Because the migrations are made BEFORE the tests, we can't actually
        # mock these values, so we just use them as they came
        USERNAME = settings.ADMIN_USERNAME
        EMAIL = settings.ADMIN_EMAIL
        PASSWORD = settings.ADMIN_PASSWORD
        self.assertEqual(USERNAME, user.get_username())
        self.assertEqual(EMAIL, user.email)
        self.assertTrue(user.check_password(PASSWORD))
