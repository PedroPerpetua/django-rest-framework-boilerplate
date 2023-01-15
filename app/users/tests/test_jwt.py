from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.tests import VALID_PASSWORD, sample_user


class TestAuthenticationFlow(TestCase):
    """Test the JWT Authentication flow with a login, refresh and logout."""

    def test(self) -> None:
        """Test the complete login flow."""
        password = VALID_PASSWORD
        user = sample_user(password=password)
        client = APIClient()

        # First, let's login the user
        login_res = client.post(reverse("users:login"), data={"email": user.email, "password": password})
        self.assertEqual(status.HTTP_200_OK, login_res.status_code)
        login_token_dict = login_res.json()
        self.assertTrue(login_token_dict["refresh"])  # Not empty
        self.assertTrue(login_token_dict["access"])  # Not empty
        # Make a call to the Whoami endpoint
        whoami_res = client.get(reverse("users:whoami"), HTTP_AUTHORIZATION=f"Bearer {login_token_dict['access']}")
        self.assertEqual(status.HTTP_200_OK, whoami_res.status_code)
        self.assertEqual({"email": user.email}, whoami_res.json())

        # Refresh the tokens
        refresh_res = client.post(reverse("users:login-refresh"), data={"refresh": login_token_dict["refresh"]})
        self.assertEqual(status.HTTP_200_OK, refresh_res.status_code)
        refresh_token_dict = refresh_res.json()
        self.assertTrue(refresh_token_dict["refresh"])  # Not empty
        self.assertTrue(refresh_token_dict["access"])  # Not empty
        # Make sure the new token is valid
        whoami_res = client.get(reverse("users:whoami"), HTTP_AUTHORIZATION=f"Bearer {login_token_dict['access']}")
        self.assertEqual(status.HTTP_200_OK, whoami_res.status_code)
        # Make sure the old token is invalid
        refresh_res = client.post(reverse("users:login-refresh"), data={"refresh": login_token_dict["refresh"]})
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, refresh_res.status_code)

        # Logout the account
        logout_res = client.post(reverse("users:logout"), data={"refresh": refresh_token_dict["refresh"]})
        self.assertEqual(status.HTTP_200_OK, logout_res.status_code)
        # Make sure the token is now invalid
        refresh_res = client.post(reverse("users:login-refresh"), data={"refresh": login_token_dict["refresh"]})
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, refresh_res.status_code)
