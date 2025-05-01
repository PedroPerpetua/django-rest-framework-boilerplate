from typing import Any
from django.urls import reverse
from rest_framework import status
from constance.test import override_config  # type: ignore[import-untyped]
from extensions.utilities.test import APITestCase
from users import serializers
from users.models import User
from users.tests import VALID_PASSWORD, sample_user


class TestUserRegisterView(APITestCase):
    """Test the UserRegisterView."""

    URL = reverse("users:register")

    @override_config(AUTH_USER_REGISTRATION_ENABLED=True)
    def test_success(self) -> None:
        """Test successfully creating a User."""
        payload = {"username": "_username", "password": VALID_PASSWORD}
        # Get the current User count
        original_count = User.objects.count()
        # Make the call
        res = self.client.post(self.URL, data=payload)
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_201_CREATED, res)
        self.assertEqual(original_count + 1, User.objects.count())
        created_user = User.objects.get(id=res.data["id"])
        self.assertResponseData(created_user, serializers.UserRegisterSerializer, res)
        # Make sure the User was created properly
        self.assertEqual(created_user.username, payload["username"])
        self.assertTrue(created_user.check_password(payload["password"]))

    @override_config(AUTH_USER_REGISTRATION_ENABLED=False)
    def test_registration_disabled_fails(self) -> None:
        """Test creating a User with the registration disabled fails."""
        payload = {"username": "_username", "password": VALID_PASSWORD}
        # Get the current User count
        original_count = User.objects.count()
        # Make the call
        res = self.client.post(
            self.URL,
            data=payload,
            HTTP_ACCEPT_LANGUAGE="en-gb",  # Set language to English to compare error message
        )
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_403_FORBIDDEN, res)
        self.assertEqual(
            {
                "type": "client_error",
                "errors": [{"code": "permission_denied", "detail": "Registration is disabled.", "attr": None}],
            },
            res.json(),
        )
        # Make sure no User was created
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
        login_res = self.client.post(self.LOGIN_URL, data={"username": user.username, "password": password})
        self.assertResponseStatusCode(status.HTTP_200_OK, login_res)
        login_token_dict = login_res.json()
        self.assertTrue(login_token_dict["refresh"])  # Not empty
        self.assertTrue(login_token_dict["access"])  # Not empty

        # Make a call to the Whoami endpoint
        whoami_res = self.client.get(
            reverse("users:whoami"), HTTP_AUTHORIZATION=f"Bearer {login_token_dict['access']}"
        )
        self.assertResponseStatusCode(status.HTTP_200_OK, whoami_res)
        self.assertEqual({"username": user.username}, whoami_res.json())

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
        res = self.client.post(reverse("users:whoami"), HTTP_AUTHORIZATION="Bearer INVALID_TOKEN")
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_401_UNAUTHORIZED, res)

    def test_login_inactive_user_fails(self) -> None:
        """Test logging in as an inactive User fails."""
        password = VALID_PASSWORD
        user = sample_user(password=password, is_active=False)
        # Make the call
        res = self.client.post(self.LOGIN_URL, data={"username": user.username, "password": password})
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_401_UNAUTHORIZED, res)

    def test_login_soft_deleted_user_fails(self) -> None:
        """Test logging in a soft deleted User fails."""
        password = VALID_PASSWORD
        user = sample_user(password=password, is_deleted=True)
        # Make the call
        res = self.client.post(self.LOGIN_URL, data={"username": user.username, "password": password})
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
        self.assertResponseData(user, serializers.UserWhoamiSerializer, res)

    def test_authentication_required(self) -> None:
        """Test that the Whoami endpoint requires an authenticated user."""
        # Make the call
        res = self.client.get(self.URL)
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_401_UNAUTHORIZED, res)


class TestUserProfileView(APITestCase):
    """Test the UserProfileView."""

    URL = reverse("users:profile")

    def setUp(self) -> None:
        self.user = sample_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_success(self) -> None:
        """Test successfully retrieving the User's profile."""
        # Make the call
        res = self.client.get(self.URL)
        # verify the response
        self.assertResponseStatusCode(status.HTTP_200_OK, res)
        self.assertResponseData(self.user, serializers.UserProfileSerializer, res)

    def test_retrieve_authentication_required(self) -> None:
        """Test that the User needs to be logged in to retrieve their profile."""
        # Create a new client that isn't logged in
        self.client.logout()
        # Make the call
        res = self.client.get(self.URL)
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_401_UNAUTHORIZED, res)

    def test_update_success(self) -> None:
        """Test successfully updating the User's profile."""
        for method in [self.client.patch, self.client.put]:
            with self.subTest(message="Test updating User profile successfully.", value=method.__name__):
                # The default UserProfileSerializer has no fields that can be updated; so we test for empty payload
                payload: dict[str, Any] = {}
                # Make the call
                res = method(self.URL, data=payload)
                # Verify the response
                self.assertResponseStatusCode(status.HTTP_200_OK, res)
                # Verify any field changes
                self.user.refresh_from_db()
                # ...

    def test_update_authentication_required(self) -> None:
        """Test that the User needs to be logged in to update their profile."""
        self.client.logout()
        for method in [self.client.patch, self.client.put]:
            with self.subTest(message="Test updating User profile without being logged in.", value=method.__name__):
                payload = {"username": f"_username_updated_{method.__name__}"}
                # Make the call
                res = method(self.URL, data=payload)
                # Verify the response
                self.assertResponseStatusCode(status.HTTP_401_UNAUTHORIZED, res)
                # Make sure the username didn't change
                self.user.refresh_from_db()
                self.assertNotEqual(payload["username"], self.user.username)


class TestUserChangePasswordView(APITestCase):
    """Test the UserChangePasswordView."""

    URL = reverse("users:change-password")

    def setUp(self) -> None:
        self.password = VALID_PASSWORD
        self.user = sample_user(password=self.password)
        self.client.force_authenticate(self.user)

    def test_success(self) -> None:
        """Test successfully changing the User's password."""
        new_password = VALID_PASSWORD + "_updated"
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
        new_password = VALID_PASSWORD + "_updated"
        wrong_password = "_" + self.password  # so it's different
        # Make the call
        res = self.client.post(
            self.URL,
            data={"password": wrong_password, "new_password": new_password},
            HTTP_ACCEPT_LANGUAGE="en-gb",  # Set language to English to compare error message
        )
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
        res = self.client.post(
            self.URL,
            data={"password": self.password, "new_password": new_password},
            HTTP_ACCEPT_LANGUAGE="en-gb",  # Set language to English to compare error message
        )
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_400_BAD_REQUEST, res)
        self.assertEqual(
            {
                "type": "validation_error",
                "errors": [
                    {
                        "code": "password_too_short",
                        "detail": "This password is too short. It must contain at least 8 characters.",
                        "attr": "non_field_errors",
                    },
                ],
            },
            res.json(),
        )
        # Make sure the password didn't change
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(new_password))
        self.assertTrue(self.user.check_password(self.password))

    def test_authentication_required(self) -> None:
        """Test that the User needs to be logged in to change the password."""
        # Create a new client that isn't logged in
        self.client.logout()
        new_password = VALID_PASSWORD + "_updated"
        # Make the call
        res = self.client.post(self.URL, data={"password": self.password, "new_password": new_password})
        # Verify the response
        self.assertResponseStatusCode(status.HTTP_401_UNAUTHORIZED, res)
        # Make sure the password didn't change
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(new_password))
        self.assertTrue(self.user.check_password(self.password))

    def test_method_not_allowed(self) -> None:
        """Because we changed the default HTTP methods, make sure the previous ones now return an error."""
        for method in [self.client.patch, self.client.put]:
            with self.subTest(msg="Testing updating password with methods not allowed.", value=method.__name__):
                new_password = VALID_PASSWORD + "_updated"
                # Make the call
                res = method(self.URL, data={"password": self.password, "new_password": new_password})
                # Verify the response
                self.assertResponseStatusCode(status.HTTP_405_METHOD_NOT_ALLOWED, res)
                # Make sure the password didn't change
                self.user.refresh_from_db()
                self.assertFalse(self.user.check_password(new_password))
                self.assertTrue(self.user.check_password(self.password))
