from django.test import TestCase
from users.models import User


class TestUser(TestCase):
    """Test the User model."""

    def test_creation(self) -> None:
        """Test creating a User object."""
        username = "_username"
        password = "_password"
        user = User.objects.create_user(username=username, password=password)
        self.assertTrue(user.check_password(password))
        self.assertEqual(f"User ({user.id}) {user.get_username()}", str(user))

    def test_creation_no_password(self) -> None:
        """Test creating a User with no password."""
        username = "_username"
        user = User.objects.create_user(username=username)
        self.assertFalse(user.has_usable_password())
