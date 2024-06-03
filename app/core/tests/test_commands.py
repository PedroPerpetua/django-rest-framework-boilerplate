from io import StringIO
from typing import Any
from unittest import TestCase as UnitTest
from unittest.mock import MagicMock, patch
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase
from core.management.commands.setup import Command as SetupCommand
from core.management.commands.startapp import Command as StartAppCommand
from core.management.commands.startapp import StartAppCommand as OriginalStartAppCommand
from core.management.commands.wait_for_db import Command as WaitForDBCommand
from extensions.utilities.test import clear_colors


class TestWaitForDBCommand(TestCase):
    """Test the wait_for_db command."""

    class MockCursor:
        def close(self) -> None: ...

    # Get the command's parameters
    RETRY_SECONDS = WaitForDBCommand.RETRY_SECONDS
    MAX_RETRIES = WaitForDBCommand.MAX_RETRIES

    @patch("django.db.backends.base.base.BaseDatabaseWrapper.cursor")
    def test_wait_for_db_ready(self, cursor_mock: MagicMock) -> None:
        """Test wait_for_db when the database is available."""
        # Setup the mock and buffers
        cursor_mock.return_value = self.MockCursor()
        output_buffer = StringIO()
        # Make the call
        call_command("wait_for_db", stdout=output_buffer)
        # Check the result
        self.assertEqual(
            "Waiting for database connection...\nDatabase connection available!\n",
            clear_colors(output_buffer.getvalue()),
        )
        # Make sure the mock was called correctly
        cursor_mock.assert_called_once()

    @patch("time.sleep")
    @patch("django.db.backends.base.base.BaseDatabaseWrapper.cursor")
    def test_wait_for_db_retry(self, cursor_mock: MagicMock, sleep_mock: MagicMock) -> None:
        """Test wait_for_db retries if database is not available."""
        if self.MAX_RETRIES == 0:  # pragma: no cover
            # No retries; nothing to test.
            self.assertTrue(True)
            return
        # Setup the mock and buffers
        cursor_mock.side_effect = ([OperationalError] * self.MAX_RETRIES) + [self.MockCursor()]
        sleep_mock.return_value = True
        output_buffer = StringIO()
        error_buffer = StringIO()
        # Make the call
        call_command("wait_for_db", stdout=output_buffer, stderr=error_buffer)
        # Check the result
        self.assertEqual(
            "Waiting for database connection...\nDatabase connection available!\n",
            clear_colors(output_buffer.getvalue()),
        )
        self.assertEqual(
            f"Connection unavailable, waiting {self.RETRY_SECONDS} second(s)...\n" * self.MAX_RETRIES,
            clear_colors(error_buffer.getvalue()),
        )
        # Make sure the mock was called correctly
        self.assertEqual(self.MAX_RETRIES + 1, cursor_mock.call_count)

    @patch("time.sleep")
    @patch("django.db.backends.base.base.BaseDatabaseWrapper.cursor")
    def test_wait_for_db_fails(self, cursor_mock: MagicMock, sleep_mock: MagicMock) -> None:
        """Test wait_for_db aborts after max retries."""
        # Setup the mock and buffers
        cursor_mock.side_effect = [OperationalError] * (self.MAX_RETRIES + 1)
        sleep_mock.return_value = True
        output_buffer = StringIO()
        error_buffer = StringIO()
        # Make the call
        call_command("wait_for_db", stdout=output_buffer, stderr=error_buffer)
        # Check the result
        self.assertEqual("Waiting for database connection...\n", clear_colors(output_buffer.getvalue()))
        self.assertEqual(
            f"Connection unavailable, waiting {self.RETRY_SECONDS} second(s)...\n" * self.MAX_RETRIES
            + f"Reached {self.MAX_RETRIES} retries with no database connection. Aborting.\n",
            clear_colors(error_buffer.getvalue()),
        )
        # Make sure the mock was called correctly
        self.assertEqual(self.MAX_RETRIES + 1, cursor_mock.call_count)


class TestSetupCommand(UnitTest):
    """Test the setup command."""

    # Get the command's parameters
    TASKS = SetupCommand.TASKS
    TASK_COUNT = len(SetupCommand.TASKS)

    @patch("core.management.commands.setup.call_command")
    def test_default(self, call_command_mock: MagicMock) -> None:
        """Test the default behavior."""
        # Setup the mock and buffers
        output_buffer = StringIO()
        error_buffer = StringIO()
        # Make the call
        call_command("setup", stdout=output_buffer, stderr=error_buffer)
        # Check the result
        expected = "Setting up app for production...\n"
        for i, (text, task) in enumerate(self.TASKS):
            # Add the expected output
            expected += f"{text} ({i}/{self.TASK_COUNT})\n"
            # Make sure the mock was called correctly
            self.assertEqual(task, call_command_mock.mock_calls[i].args)
        expected += f"Finished Setup! ({self.TASK_COUNT}/{self.TASK_COUNT})\n"
        self.assertEqual(expected, clear_colors(output_buffer.getvalue()))
        # Make sure the mock was called the right number of times
        self.assertEqual(self.TASK_COUNT, call_command_mock.call_count)


class TestStartAppCommand(UnitTest):
    """Test the customized startapp command."""

    # Get the command's parameters
    TEMPLATE_PATH = str(StartAppCommand.TEMPLATE_PATH)

    @patch.object(OriginalStartAppCommand, "handle")
    def test_default(self, handle_mock: MagicMock) -> None:
        """Test the default behavior of not passing in a template."""
        app_name = "_app_name"
        # Setup the mock and buffers
        handle_mock.return_value = None
        output_buffer = StringIO()
        error_buffer = StringIO()
        # Make the call
        call_command("startapp", app_name, stdout=output_buffer, stderr=error_buffer)
        # Make sure the mock was called correctly
        handle_mock.assert_called_once()
        kwargs: dict[str, Any] = handle_mock.call_args.kwargs
        self.assertIn("template", kwargs)
        self.assertEqual(self.TEMPLATE_PATH, kwargs["template"])
        self.assertIn("name", kwargs)
        self.assertEqual(app_name, kwargs["name"])

    @patch.object(OriginalStartAppCommand, "handle")
    def test_override(self, handle_mock: MagicMock) -> None:
        """Test that passing the template option overrides our default."""
        app_name = "_app_name"
        template = "_template"
        # Setup the mock and buffers
        handle_mock.return_value = None
        output_buffer = StringIO()
        error_buffer = StringIO()
        # Make the call
        call_command("startapp", app_name, template=template, stdout=output_buffer, stderr=error_buffer)
        # Make sure the mock was called correctly
        handle_mock.assert_called_once()
        kwargs: dict[str, Any] = handle_mock.call_args.kwargs
        self.assertIn("template", kwargs)
        self.assertEqual(template, kwargs["template"])
        self.assertIn("name", kwargs)
        self.assertEqual(app_name, kwargs["name"])
