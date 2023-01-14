from django.core.exceptions import ValidationError
from django.test import TestCase
from users.models import User
from users.tests import generate_invalid_password, generate_valid_password, sample_user


class TestUserModel(TestCase):
    """Test our custom User model."""

    def test_create_user(self) -> None:
        """Test creation and string/repr representation."""
        email = "_email@example.com"
        password = generate_valid_password()
        user = User.objects.create_user(email=email, password=password)
        self.assertEqual(email, user.email)
        self.assertEqual(email, user.get_username())  # Make sure the email is the username field
        self.assertTrue(user.check_password(password))
        # By default it's not an admin
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        # String representation
        self.assertEqual(f"User ({user.id}) {email}", str(user))

    def test_create_superuser(self) -> None:
        """Test creating a superuser."""
        email = "_email@example.com"
        password = generate_valid_password()
        user = User.objects.create_superuser(email=email, password=password)
        self.assertEqual(email, user.email)
        self.assertEqual(email, user.get_username())  # Make sure the email is the username field
        self.assertTrue(user.check_password(password))
        # It's now an admin
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        # string representation
        self.assertEqual(f"User ({user.id}) {email}", str(user))

    def test_email_normalized(self) -> None:
        """Test that emails are normalized for new users."""
        sample_emails = [
            ("test1@EXAMPLE.com", "test1@example.com"),
            ("TEST2@example.com", "TEST2@example.com"),
            ("TEST3@EXAMPLE.com", "TEST3@example.com"),
            ("test4@example.COM", "test4@example.com"),
        ]
        for email, expected in sample_emails:
            with self.subTest(msg="Checking if email is normalized.", email=email, expected=expected):
                user = sample_user(email=email)
                self.assertEqual(expected, user.email)

    def test_email_changes_normalized(self) -> None:
        """Test that emails are normalized when updating a user."""
        user = sample_user(email="_email@example.com")
        email, expected = ("test1@EXAMPLE.com", "test1@example.com")
        user.email = email
        user.save()
        self.assertEqual(expected, user.email)

    def test_email_required(self) -> None:
        """Test that user's email is required for new users."""
        for value in ["", " ", "\n"]:  # Different empty values
            with self.subTest(msg="Checking if value raises ValidationError.", value=value):
                with self.assertRaises(ValidationError) as ve_ctx:
                    sample_user(email=value)
                ve = ve_ctx.exception
                self.assertEqual("Email cannot be empty.", ve.message)
        with self.subTest(msg="Checking if None raises ValueError.", value=None):
            # This test is slightly different because sample_user with `email=None` generates one
            with self.assertRaises(ValidationError) as ve_ctx:
                User.objects.create(email=value)
            ve = ve_ctx.exception
            self.assertEqual("Email cannot be empty.", ve.message)
