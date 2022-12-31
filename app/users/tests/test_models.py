from django.test import TestCase
from users.models import User


class TestUserModel(TestCase):
    """Test our custom User model."""

    def test_str_repr(self):
        """Test creation and string/repr representation."""
        email = "_email@example.com"
        password = "_password"
        user = User.objects.create_user(email=email, password=password)
        self.assertEqual(email, user.email)
        self.assertEqual(email, user.get_username()) # Make sure the email is the username field
        self.assertTrue(user.check_password(password))
        self.assertEqual(f"User ({user.id}) {email}", str(user))
        self.assertEqual(f"User { {'id': user.id, 'email': email} }", repr(user))
