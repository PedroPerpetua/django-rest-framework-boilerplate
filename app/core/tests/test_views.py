from django.urls import reverse
from rest_framework import status
from extensions.utilities.test import APITestCase


class TestCoreAPI(APITestCase):
    """Test the Core API endpoints."""

    def test_ping(self) -> None:
        """Test the ping endpoint."""
        res = self.client.get(reverse("ping"))
        self.assertResponseStatusCode(status.HTTP_200_OK, res)
        self.assertEqual("pong", res.json())
