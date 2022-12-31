from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class TestCoreAPI(TestCase):
    """Test the Core API endpoints."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_ping(self) -> None:
        """Test the ping endpoint."""
        res = self.client.get(reverse("ping"))
        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEqual("pong", res.json())
