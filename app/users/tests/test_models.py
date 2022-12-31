from django.test import TestCase
from users.models import User
from users.tests import sample_user


class TestUserModel(TestCase):
    """Test our custom User model."""

    def test_str_repr(self) -> None:
        """Test creation and string/repr representation."""
        email = "_email@example.com"
        password = "_password"
        user = User.objects.create_user(email=email, password=password)
        self.assertEqual(email, user.email)
        self.assertEqual(email, user.get_username())  # Make sure the email is the username field
        self.assertTrue(user.check_password(password))
        self.assertEqual(f"User ({user.id}) {email}", str(user))
        self.assertEqual(f"User { {'id': user.id, 'email': email} }", repr(user))

    def test_email_normalized(self) -> None:
        """Test that emails are normalized for new users."""
        sample_emails = [
            ("test1@EXAMPLE.com", "test1@example.com"),
            ("TEST2@example.com", "TEST2@example.com"),
            ("TEST3@EXAMPLE.com", "TEST3@example.com"),
            ("test4@example.COM", "test4@example.com"),
        ]
        for email, expected in sample_emails:
            user = sample_user(email=email)
            self.assertEqual(expected, user.email)
