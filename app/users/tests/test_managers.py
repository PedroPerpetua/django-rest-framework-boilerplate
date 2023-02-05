from unittest import skipIf
from django.test import TestCase
from core.utilities import uuid
from users.managers import UserManager
from users.models import User
from users.tests import VALID_PASSWORD, generate_valid_username


@skipIf(not isinstance(User.objects, UserManager), "Different UserManager applied.")
class TestUserManager(TestCase):
    """
    Test the UserManager. To do this, we use our user model. These tests are skipped if the current user model uses a
    different UserManager.
    """

    def test_create_user(self) -> None:
        """Test creating a normal user."""
        password = VALID_PASSWORD
        # Generate values for possible username fields
        username = generate_valid_username("username")
        email = generate_valid_username("email")
        user = User.objects.create_user(username=username, email=email, password=password)
        self.assertNotEqual(password, user.password)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_pops_unknown_fields(self) -> None:
        """Test creating a normal user pops fields not present in the user."""
        field_name = uuid()
        value = "_value"
        password = VALID_PASSWORD
        # Generate values for possible username fields
        username = generate_valid_username("username")
        email = generate_valid_username("email")
        # If it doesn't pop, this line would raise an exception
        user = User.objects.create_user(username=username, email=email, password=password, **{field_name: value})
        self.assertFalse(hasattr(user, field_name))

    def test_create_superuser(self) -> None:
        """Test creating a superuser."""
        password = VALID_PASSWORD
        # Generate values for possible username fields
        username = generate_valid_username("username")
        email = generate_valid_username("email")
        user = User.objects.create_superuser(username=username, email=email, password=password)
        self.assertNotEqual(password, user.password)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_superuser_forces_staff(self) -> None:
        """Test creating a superuser forces the user to be staff."""
        password = VALID_PASSWORD
        # Generate values for possible username fields
        username = generate_valid_username("username")
        email = generate_valid_username("email")
        user = User.objects.create_superuser(
            username=username, email=email, password=password, is_staff=False, is_superuser=False
        )
        self.assertNotEqual(password, user.password)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
