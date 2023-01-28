from unittest import TestCase
from core.utilities.test import MockResponse


class TestTestUtilities(TestCase):
    """Test the test utilities provided"""

    def test_MockResponse(self) -> None:
        """Test the MockResponse class."""
        with self.subTest("Test creating a MockResponse object."):
            code = 200
            json = {"_key", "_value"}
            obj = MockResponse(code, json)
            self.assertEqual(code, obj.status_code)
            self.assertEqual(json, obj.json())
            self.assertEqual(str(json), obj.text)
        with self.subTest("Test the `ok` property."):
            self.assertFalse(MockResponse(100).ok)
            self.assertTrue(MockResponse(200).ok)
            self.assertFalse(MockResponse(400).ok)
