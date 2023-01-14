from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User
from users.tests import generate_invalid_password, generate_valid_password, sample_user


@override_settings(AUTH_USER_REGISTRATION_ENABLED=True)  # For testing purposes assume it's True
class TestUserRegisterView(TestCase):
    """Test the UserRegisterView."""
    URL = reverse("users:register")

    def setUp(self) -> None:
        self.client = APIClient()

    def test_success(self) -> None:
        """Test successfully creating an user."""
        # Get the current user count
        original_count = User.objects.count()
        # Make the call
        email = "_email@example.com"
        password = generate_valid_password()
        res = self.client.post(self.URL, data={"email": email, "password": password})
        # Verify the response
        self.assertEqual(status.HTTP_201_CREATED, res.status_code)
        self.assertEqual({"email": email}, res.json())
        # Make sure the user was created properly
        self.assertEqual(original_count + 1, User.objects.count())
        user_filter = User.objects.filter(email=email)
        self.assertTrue(user_filter.exists())
        user = user_filter.get()
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    @override_settings(AUTH_USER_REGISTRATION_ENABLED=False)
    def test_registration_disabled_fails(self) -> None:
        """Test creating an user with the registration disabled fails."""
        # Get the current user count
        original_count = User.objects.count()
        res = self.client.post(self.URL, data={"email": "_email@example.com", "password": generate_valid_password()})
        # Verify the response
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)
        content = res.json()
        self.assertEqual("REG_DISABLED", content["errcode"])
        self.assertEqual("Registration is disabled.", content["error"])
        # Make sure no user was created
        self.assertEqual(original_count, User.objects.count())


class TestUserChangePasswordView(TestCase):
    """Test the UserChangePasswordView."""
    URL = reverse("users:change-password")

    def setUp(self) -> None:
        self.password = generate_valid_password()
        self.user = sample_user(password=self.password)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_success(self) -> None:
        """Test successfully changing a user's password."""
        # Make the call
        new_password = generate_valid_password()
        res = self.client.post(self.URL, data={"password": self.password, "new_password": new_password})
        # Verify the response
        self.assertEqual(status.HTTP_204_NO_CONTENT, res.status_code)
        self.assertEqual(0, len(res.content))  # empty response
        # Make sure the password changed
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(self.password))
        self.assertTrue(self.user.check_password(new_password))

    def test_wrong_password(self) -> None:
        """Test that using the wrong password fails."""
        # Make the call
        new_password = generate_valid_password()
        wrong_password = generate_valid_password()  # It'll be a different one
        res = self.client.post(self.URL, data={"password": wrong_password, "new_password": new_password})
        # Verify the response
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)
        content = res.json()
        self.assertEqual("WRONG_PASSWORD", content["errcode"])
        self.assertEqual("The original password is wrong.", content["error"])
        # Make sure the password didn't change
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(new_password))
        self.assertTrue(self.user.check_password(self.password))

    def test_bad_password(self) -> None:
        """Test that using an invalid password for the new password fails."""
        # Make the call
        new_password = generate_invalid_password()
        res = self.client.post(self.URL, data={"password": self.password, "new_password": new_password})
        # Verify the response
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)
        content = res.json()
        self.assertEqual("INVALID_PASSWORD", content["errcode"])
        self.assertEqual("The new password is invalid.", content["error"])
        # Make sure the password didn't change
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(new_password))
        self.assertTrue(self.user.check_password(self.password))

    def test_authentication_required(self) -> None:
        """Test that the user needs to be logged in to change the password."""
        # Create a new client that isn't logged in
        client = APIClient()
        # Make the call
        new_password = generate_valid_password()
        res = client.post(self.URL, data={"password": self.password, "new_password": new_password})
        # Verify the response
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, res.status_code)
        # Make sure the password didn't change
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(new_password))
        self.assertTrue(self.user.check_password(self.password))
