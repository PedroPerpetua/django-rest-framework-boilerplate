from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from users import serializers
from users.models import User
from users.tests import INVALID_PASSWORD, VALID_PASSWORD, generate_valid_email, sample_user


@override_settings(AUTH_USER_REGISTRATION_ENABLED=True)  # For testing purposes assume it's True
class TestUserRegisterView(APITestCase):
    """Test the UserRegisterView."""

    URL = reverse("users:register")

    def setUp(self) -> None:
        self.client = APIClient()

    def test_success(self) -> None:
        """Test successfully creating an user."""
        # Get the current user count
        original_count = User.objects.count()
        # Make the call
        email = generate_valid_email()
        password = VALID_PASSWORD
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
        res = self.client.post(self.URL, data={"email": generate_valid_email(), "password": VALID_PASSWORD})
        # Verify the response
        self.assertEqual(status.HTTP_403_FORBIDDEN, res.status_code)
        self.assertEqual("Registration is disabled.", res.json()["errors"][0]["detail"])
        # Make sure no user was created
        self.assertEqual(original_count, User.objects.count())


class TestUserWhoamiView(APITestCase):
    """Test the UserWhoamiView."""

    URL = reverse("users:whoami")

    def setUp(self) -> None:
        self.client = APIClient()

    def test_success(self) -> None:
        # Create and login a user
        user = sample_user()
        self.client.force_authenticate(user)
        # Make the call
        res = self.client.get(self.URL)
        # Verify the response
        self.assertEqual(status.HTTP_200_OK, res.status_code)
        expected = serializers.UserWhoamiSerializer(user).data
        self.assertEqual(expected, res.json())

    def test_requires_authorization(self) -> None:
        # Make the call
        res = self.client.get(self.URL)
        # Verify the response
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, res.status_code)


class TestUserProfileView(APITestCase):
    """Test the UserProfileView."""

    URL = reverse("users:profile")

    def setUp(self) -> None:
        self.user = sample_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_get_success(self) -> None:
        """Test successfully retrieving the user's profile."""
        # Make the call
        res = self.client.get(self.URL)
        # verify the response
        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEqual(serializers.UserProfileSerializer(self.user).data, res.json())

    def test_get_authentication_required(self) -> None:
        """Test that the user needs to be logged in to retrieve their profile."""
        # Create a new client that isn't logged in
        client = APIClient()
        # Make the call
        res = client.get(self.URL)
        # Verify the response
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, res.status_code)

    def test_update_success(self) -> None:
        """Test successfully updating the user's profile."""
        for func in [self.client.patch, self.client.put]:
            with self.subTest(msg="Updating the user's profile.", value=func.__name__):
                # Make the call
                payload = {"email": generate_valid_email()}
                res = func(self.URL, data=payload)
                # Verify the response
                self.assertEqual(status.HTTP_200_OK, res.status_code)
                # Make sure the email changed
                self.user.refresh_from_db()
                self.assertEqual(payload["email"], self.user.email)

    def test_update_fails(self) -> None:
        """Test that updating the user's profile with bad data fails."""
        for func in [self.client.patch, self.client.put]:
            with self.subTest(msg="Updating the user's profile.", value=func.__name__):
                # Make the call
                payload = {"email": "_invalid_email"}
                res = func(self.URL, data=payload)
                # Verify the response
                self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)
                self.assertEqual(
                    {"errors": [{"code": "invalid", "detail": "Enter a valid email address.", "attr": "email"}]},
                    res.json(),
                )
                # Make sure the email didn't change change
                self.user.refresh_from_db()
                self.assertNotEqual(payload["email"], self.user.email)

    def test_update_authentication_required(self) -> None:
        """Test that the user needs to be logged in to update their profile."""
        client = APIClient()
        for func in [client.patch, client.put]:
            with self.subTest(msg="Updating the user's profile.", value=func.__name__):
                # Make the call
                payload = {"email": generate_valid_email()}
                res = func(self.URL, data=payload)
                # Verify the response
                self.assertEqual(status.HTTP_401_UNAUTHORIZED, res.status_code)
                # Make sure the email didn't change
                self.user.refresh_from_db()
                self.assertNotEqual(payload["email"], self.user.email)


class TestUserChangePasswordView(APITestCase):
    """Test the UserChangePasswordView."""

    URL = reverse("users:change-password")

    def setUp(self) -> None:
        self.password = VALID_PASSWORD
        self.user = sample_user(password=self.password)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_success(self) -> None:
        """Test successfully changing a user's password."""
        # Make the call
        new_password = "new" + VALID_PASSWORD
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
        new_password = "new" + VALID_PASSWORD
        wrong_password = "_" + self.password  # so it's different
        res = self.client.post(self.URL, data={"password": wrong_password, "new_password": new_password})
        # Verify the response
        self.assertEqual(status.HTTP_403_FORBIDDEN, res.status_code)
        self.assertEqual(
            {"errors": [{"code": "permission_denied", "detail": "Wrong Password", "attr": None}]}, res.json()
        )
        # Make sure the password didn't change
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(new_password))
        self.assertTrue(self.user.check_password(self.password))

    def test_bad_password(self) -> None:
        """Test that using an invalid password for the new password fails."""
        # Make the call
        new_password = INVALID_PASSWORD
        res = self.client.post(self.URL, data={"password": self.password, "new_password": new_password})
        # Verify the response
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)
        errors = res.json()["errors"]
        self.assertEqual(1, len(errors))
        error = errors[0]
        self.assertIsNone(error["attr"])
        self.assertEqual("invalid", error["code"])
        self.assertIsInstance(error["detail"], str)
        # Make sure the password didn't change
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(new_password))
        self.assertTrue(self.user.check_password(self.password))

    def test_authentication_required(self) -> None:
        """Test that the user needs to be logged in to change the password."""
        # Create a new client that isn't logged in
        client = APIClient()
        # Make the call
        new_password = "new" + VALID_PASSWORD
        res = client.post(self.URL, data={"password": self.password, "new_password": new_password})
        # Verify the response
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, res.status_code)
        # Make sure the password didn't change
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(new_password))
        self.assertTrue(self.user.check_password(self.password))

    def test_method_not_allowed(self) -> None:
        """Because we changed the default HTTP methods, make sure the previous now return an error."""
        for func in [self.client.patch, self.client.put]:
            with self.subTest(msg="Testing updating password with methods not allowed.", value=func.__name__):
                # Make the call
                new_password = "new" + VALID_PASSWORD
                res = func(self.URL, data={"password": self.password, "new_password": new_password})
                # Verify the response
                self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, res.status_code)
                # Make sure the password didn't change
                self.user.refresh_from_db()
                self.assertFalse(self.user.check_password(new_password))
                self.assertTrue(self.user.check_password(self.password))
