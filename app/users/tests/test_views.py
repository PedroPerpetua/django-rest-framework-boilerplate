from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User


@override_settings(AUTH_USER_REGISTRATION_ENABLED=True)  # For testing purposes assume it's True
class TestUserRegisterView(TestCase):
    """Test the UserRegisterView."""
    URL = reverse("users:register")

    def setUp(self) -> None:
        self.client = APIClient()

    def test_success(self):
        """Test successfully creating an user."""
        # Get the current user count
        original_count = User.objects.count()
        # Make the call
        email = "_email@example.com"
        password = "_password"
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
    def test_registration_disabled_fails(self):
        """Test creating an user with the registration disabled fails."""
        # Get the current user count
        original_count = User.objects.count()
        res = self.client.post(self.URL, data={"email": "_email@example.com", "password": "_password"})
        # Verify the response
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)
        content = res.json()
        self.assertEqual("REG_DISABLED", content["errcode"])
        self.assertEqual("Registration is disabled.", content["error"])
        # Make sure no user was created
        self.assertEqual(original_count, User.objects.count())
