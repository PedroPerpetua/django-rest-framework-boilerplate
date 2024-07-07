from unittest.mock import MagicMock, patch
from django.core.exceptions import ValidationError as DjangoValidationError
from django.urls import reverse
from rest_framework import status
from extensions.utilities.test import APITestCase


class TestExceptionHandler(APITestCase):
    """Test the ExceptionHandler."""

    @patch("core.views.PingView.get")
    def test_validation_error(self, view_mock: MagicMock) -> None:
        """Test that Django ValidationErrors are correctly converted to DRF ValidationErrors."""
        # Set up the mock
        exc_code = "_code"
        exc_message = "_message"
        view_mock.side_effect = DjangoValidationError(exc_message, code=exc_code)
        # Use the ping view for testing purposes
        res = self.client.get(reverse("ping"))
        self.assertResponseStatusCode(status.HTTP_400_BAD_REQUEST, res)
        self.assertEqual(
            {
                "type": "validation_error",
                "errors": [{"detail": exc_message, "code": exc_code, "attr": "non_field_errors"}],
            },
            res.json(),
        )
