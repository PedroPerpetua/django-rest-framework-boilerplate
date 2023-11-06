from unittest import skipIf
from django.test import TestCase
from core.utilities import uuid
from users.managers import UserManager
from users.models import User
from users.tests import VALID_PASSWORD


@skipIf(not isinstance(User.objects, UserManager), "Different UserManager applied.")
class TestUserManager(TestCase):
    """
    Test the UserManager. To do this, we use our user model. These tests are skipped if the current user model uses a
    different UserManager.
    """

    def test_create_user(self) -> None:
        """Test creating a normal user."""
        username = uuid()
        password = VALID_PASSWORD
        user = User.objects.create_user(username=username, password=password)
        self.assertEqual(username, user.username)
        self.assertNotEqual(password, user.password)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self) -> None:
        """Test creating a superuser."""
        username = uuid()
        password = VALID_PASSWORD
        user = User.objects.create_superuser(username=username, password=password)
        self.assertEqual(username, user.username)
        self.assertNotEqual(password, user.password)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_superuser_forces_staff(self) -> None:
        """Test creating a superuser forces the user to be staff."""
        username = uuid()
        password = VALID_PASSWORD
        user = User.objects.create_superuser(username=username, password=password, is_staff=False, is_superuser=False)
        self.assertEqual(username, user.username)
        self.assertNotEqual(password, user.password)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
