from io import StringIO
from unittest.mock import MagicMock, patch
from django.test import TestCase
from django.db.utils import OperationalError
from django.core.management import call_command
from core.tests.utils import clear_colors
from core.management.commands.wait_for_db import Command as WaitForDBCommand


class TestWaitForDBCommand(TestCase):
    """Test the wait_for_db command."""
    # Get the command's parameters
    RETRY_SECONDS = WaitForDBCommand.RETRY_SECONDS
    MAX_RETRIES = WaitForDBCommand.MAX_RETRIES

    def test_wait_for_db_ready(self):
        """Test waiting for db when db is available."""
        output_buffer = StringIO()
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.return_value = True
            call_command("wait_for_db", stdout=output_buffer)
            self.assertEqual(gi.call_count, 1)
            self.assertEqual(
                "Waiting for database connection...\n"
                "Database connection available!\n",
                clear_colors(output_buffer.getvalue())
            )

    @patch("time.sleep", return_value=True)
    def test_wait_for_db_retry(self, mock_sleep: MagicMock):
        """Test waiting for db retries."""
        if self.MAX_RETRIES == 0: # type: ignore - MAX_RETRIES is set by user
            # No retries; nothing to test.
            self.assertTrue(True)
            return
        output_buffer = StringIO()
        error_buffer = StringIO()
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.side_effect = ([OperationalError] * self.MAX_RETRIES) + [True]
            call_command(
                "wait_for_db",
                stdout=output_buffer, stderr=error_buffer
            )
            self.assertEqual(gi.call_count, self.MAX_RETRIES + 1)
            self.assertEqual(
                "Waiting for database connection...\n"
                "Database connection available!\n",
                clear_colors(output_buffer.getvalue())
            )
            self.assertEqual(
                f"Connection unavailable, waiting {self.RETRY_SECONDS} "
                "second(s)...\n" * self.MAX_RETRIES,
                clear_colors(error_buffer.getvalue())
            )

    @patch("time.sleep", return_value=True)
    def test_wait_for_db_fails(self, mock_sleep: MagicMock):
        """Test waiting for db fails."""
        output_buffer = StringIO()
        error_buffer = StringIO()
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.side_effect = ([OperationalError] * (self.MAX_RETRIES + 1))
            call_command(
                "wait_for_db",
                stdout=output_buffer, stderr=error_buffer
            )
            self.assertEqual(gi.call_count, self.MAX_RETRIES + 1)
            self.assertEqual(
                "Waiting for database connection...\n",
                clear_colors(output_buffer.getvalue())
            )
            self.assertEqual(
                f"Connection unavailable, waiting {self.RETRY_SECONDS} "
                "second(s)...\n" * self.MAX_RETRIES +
                f"Reached {self.MAX_RETRIES} retries with no database "
                "connection. Aborting.\n",
                clear_colors(error_buffer.getvalue())
            )
