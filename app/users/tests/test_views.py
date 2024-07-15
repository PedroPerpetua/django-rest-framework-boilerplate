from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from extensions.utilities import uuid
from extensions.utilities.test import APITestCase
from users import serializers
from users.models import User
from users.tests import VALID_PASSWORD, sample_user


@override_settings(AUTH_USER_REGISTRATION_ENABLED=True)  # For testing purposes assume it's True
class TestUserRegisterView(APITestCase):
    """Test the UserRegisterView."""

    URL = reverse("users:register")

    def test_success(self) -> None:
        """Test successfully creating a user."""
        # Get the current user count
        original_count = User.objects.count()
        # Make the call
        username = uuid()
        password = VALID_PASSWORD
        res = self.client.post(self.URL, data={"username": username, "password": password})
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_201_CREATED, res)
        self.assertEqual(original_count + 1, User.objects.count())
        created_user = User.objects.get(id=res.data["id"])
        self.assertEqual(serializers.UserRegisterSerializer(created_user).data, res.json())
        # Make sure the user was created properly
        self.assertEqual(created_user.username, username)
        self.assertTrue(created_user.check_password(password))

    @override_settings(AUTH_USER_REGISTRATION_ENABLED=False)
    def test_registration_disabled_fails(self) -> None:
        """Test creating a user with the registration disabled fails."""
        # Get the current user count
        original_count = User.objects.count()
        username = uuid()
        password = VALID_PASSWORD
        # Make the call
        res = self.client.post(self.URL, data={"username": username, "password": password})
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_403_FORBIDDEN, res)
        self.assertEqual("Registration is disabled.", res.json()["errors"][0]["detail"])
        # Make sure no user was created
        self.assertEqual(original_count, User.objects.count())


class TestAuthentication(APITestCase):
    """
    Test the JWT Authentication flow with a login, refresh and logout.

    These tests cover the UserLoginView, UserLoginRefreshView, UserLogoutView.
    """

    LOGIN_URL = reverse("users:login")

    def test_auth_flow(self) -> None:
        """Test the complete login flow."""
        password = VALID_PASSWORD
        user = sample_user(password=password)

        # First, let's login the user
        login_res = self.client.post(self.LOGIN_URL, data={"username": user.get_username(), "password": password})
        self.assertResponseStatusCode(status.HTTP_200_OK, login_res)
        login_token_dict = login_res.json()
        self.assertTrue(login_token_dict["refresh"])  # Not empty
        self.assertTrue(login_token_dict["access"])  # Not empty

        # Make a call to the Whoami endpoint
        whoami_res = self.client.get(
            reverse("users:whoami"), HTTP_AUTHORIZATION=f"Bearer {login_token_dict['access']}"
        )
        self.assertResponseStatusCode(status.HTTP_200_OK, whoami_res)
        self.assertEqual({"username": user.get_username()}, whoami_res.json())

        # Refresh the tokens
        refresh_res = self.client.post(reverse("users:login-refresh"), data={"refresh": login_token_dict["refresh"]})
        self.assertResponseStatusCode(status.HTTP_200_OK, refresh_res)
        refresh_token_dict = refresh_res.json()
        self.assertTrue(refresh_token_dict["refresh"])  # Not empty
        self.assertTrue(refresh_token_dict["access"])  # Not empty
        # Make sure the new token is valid
        whoami_res = self.client.get(
            reverse("users:whoami"), HTTP_AUTHORIZATION=f"Bearer {login_token_dict['access']}"
        )
        self.assertResponseStatusCode(status.HTTP_200_OK, whoami_res)
        # Make sure the old token is invalid
        refresh_res = self.client.post(reverse("users:login-refresh"), data={"refresh": login_token_dict["refresh"]})
        self.assertResponseStatusCode(status.HTTP_401_UNAUTHORIZED, refresh_res)

        # Logout the user
        logout_res = self.client.post(reverse("users:logout"), data={"refresh": refresh_token_dict["refresh"]})
        self.assertResponseStatusCode(status.HTTP_200_OK, logout_res)
        # Make sure the token is now invalid
        refresh_res = self.client.post(reverse("users:login-refresh"), data={"refresh": login_token_dict["refresh"]})
        self.assertResponseStatusCode(status.HTTP_401_UNAUTHORIZED, refresh_res)

    def test_invalid_token(self) -> None:
        """Test making a request with an invalid token (as opposed to no token at all)."""
        # Make the call
        res = self.client.post(reverse("users:whoami"), HTTP_AUTHORIZATION=f"Bearer INVALID_TOKEN")
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_401_UNAUTHORIZED, res)

    def test_login_inactive_user_fails(self) -> None:
        """Test logging in as an inactive user fails."""
        password = VALID_PASSWORD
        user = sample_user(password=password, is_active=False)
        # Make the call
        res = self.client.post(self.LOGIN_URL, data={"username": user.get_username(), "password": password})
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_401_UNAUTHORIZED, res)

    def test_login_soft_deleted_user_fails(self) -> None:
        """Test logging in a soft deleted user fails."""
        password = VALID_PASSWORD
        user = sample_user(password=password)
        user.soft_delete()
        # Make the call
        res = self.client.post(self.LOGIN_URL, data={"username": user.get_username(), "password": password})
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_401_UNAUTHORIZED, res)


class TestUserWhoamiView(APITestCase):
    """Test the UserWhoamiView."""

    URL = reverse("users:whoami")

    def test_success(self) -> None:
        """Test successfully calling the Whoami endpoint."""
        # Create and login a user
        user = sample_user()
        self.client.force_authenticate(user)
        # Make the call
        res = self.client.get(self.URL)
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_200_OK, res)
        expected = serializers.UserWhoamiSerializer(user).data
        self.assertEqual(expected, res.json())

    def test_requires_authorization(self) -> None:
        """Test that the Whoami endpoint requires authorization."""
        # Make the call
        res = self.client.get(self.URL)
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_401_UNAUTHORIZED, res)

    def test_requires_active(self) -> None:
        """Test that the Whoami endpoint requires an active user."""
        # Create and login an inactive user
        user = sample_user(is_active=False)
        self.client.force_authenticate(user)
        # Make the call
        res = self.client.get(self.URL)
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_403_FORBIDDEN, res)

    def test_requires_not_soft_deleted(self) -> None:
        """Test that the Whoami endpoint requires a not soft-deleted user."""
        # Create and soft-delete a user
        user = sample_user()
        user.soft_delete()
        self.client.force_authenticate(user)
        # Make the call
        res = self.client.get(self.URL)
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_403_FORBIDDEN, res)


class TestUserProfileView(APITestCase):
    """Test the UserProfileView."""

    URL = reverse("users:profile")

    def setUp(self) -> None:
        self.user = sample_user()
        self.client.force_authenticate(self.user)

    def test_get_success(self) -> None:
        """Test successfully retrieving the user's profile."""
        # Make the call
        res = self.client.get(self.URL)
        # verify the response
        self.assertResponseStatusCode(status.HTTP_200_OK, res)
        self.assertEqual(serializers.UserProfileSerializer(self.user).data, res.json())

    def test_get_authentication_required(self) -> None:
        """Test that the user needs to be logged in to retrieve their profile."""
        # Create a new client that isn't logged in
        client = APIClient()
        # Make the call
        res = client.get(self.URL)
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_401_UNAUTHORIZED, res)

    def test_update_success(self) -> None:
        """Test successfully updating the user's profile."""
        payload = {"username": "new_username"}
        # Make the call
        res = self.client.patch(self.URL, data=payload)
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_200_OK, res)
        # Make sure the username changed
        self.user.refresh_from_db()
        self.assertEqual(payload["username"], self.user.get_username())

    def test_update_fails(self) -> None:
        """Test that updating the user's profile with bad data fails."""
        payload = {"username": ""}
        # Make the call
        res = self.client.patch(self.URL, data=payload)
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_400_BAD_REQUEST, res)
        self.assertEqual(
            {
                "type": "validation_error",
                "errors": [{"code": "blank", "detail": "This field may not be blank.", "attr": "username"}],
            },
            res.json(),
        )
        # Make sure it didn't change
        self.user.refresh_from_db()
        self.assertNotEqual(payload["username"], self.user.get_username())

    def test_update_authentication_required(self) -> None:
        """Test that the user needs to be logged in to update their profile."""
        client = APIClient()
        payload = {"username": "new_username"}
        # Make the call
        res = client.patch(self.URL, data=payload)
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_401_UNAUTHORIZED, res)
        # Make sure the username didn't change
        self.user.refresh_from_db()
        self.assertNotEqual(payload["username"], self.user.get_username())


class TestUserChangePasswordView(APITestCase):
    """Test the UserChangePasswordView."""

    URL = reverse("users:change-password")

    def setUp(self) -> None:
        self.password = VALID_PASSWORD
        self.user = sample_user(password=self.password)
        self.client.force_authenticate(self.user)

    def test_success(self) -> None:
        """Test successfully changing a user's password."""
        new_password = "new" + VALID_PASSWORD
        # Make the call
        res = self.client.post(self.URL, data={"password": self.password, "new_password": new_password})
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_204_NO_CONTENT, res)
        self.assertEqual(0, len(res.content))  # empty response
        # Make sure the password changed
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(self.password))
        self.assertTrue(self.user.check_password(new_password))

    def test_wrong_password(self) -> None:
        """Test that using the wrong password fails."""
        new_password = "new" + VALID_PASSWORD
        wrong_password = "_" + self.password  # so it's different
        # Make the call
        res = self.client.post(self.URL, data={"password": wrong_password, "new_password": new_password})
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_401_UNAUTHORIZED, res)
        self.assertEqual(
            {
                "type": "client_error",
                "errors": [{"code": "authentication_failed", "detail": "Wrong password.", "attr": None}],
            },
            res.json(),
        )
        # Make sure the password didn't change
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(new_password))
        self.assertTrue(self.user.check_password(self.password))

    def test_bad_password(self) -> None:
        """Test that using an invalid password for the new password fails."""
        new_password = "short"
        # Make the call
        res = self.client.post(self.URL, data={"password": self.password, "new_password": new_password})
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_400_BAD_REQUEST, res)
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
        new_password = "new" + VALID_PASSWORD
        # Make the call
        res = client.post(self.URL, data={"password": self.password, "new_password": new_password})
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_401_UNAUTHORIZED, res)
        # Make sure the password didn't change
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(new_password))
        self.assertTrue(self.user.check_password(self.password))

    def test_method_not_allowed(self) -> None:
        """Because we changed the default HTTP methods, make sure the previous now return an error."""
        for func in [self.client.patch, self.client.put]:
            with self.subTest(msg="Testing updating password with methods not allowed.", value=func.__name__):
                new_password = "new" + VALID_PASSWORD
                # Make the call
                res = func(self.URL, data={"password": self.password, "new_password": new_password})
                # Verify the response
                self.assertResponseStatusCode(status.HTTP_405_METHOD_NOT_ALLOWED, res)
                # Make sure the password didn't change
                self.user.refresh_from_db()
                self.assertFalse(self.user.check_password(new_password))
                self.assertTrue(self.user.check_password(self.password))
