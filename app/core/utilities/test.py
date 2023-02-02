import re
from typing import Any
import requests
from django.db import connection
from django.db.models import Model
from django.test import TestCase
from core.utilities.types import JSON_BASE


class AbstractModelTestCase(TestCase):
    """
    Test case class to generate a new model from an abstract at runtime.

    Adapted from: https://michael.mior.ca/blog/unit-testing-django-model-mixins/
    """

    MODEL: Type[Model] = None  # type: ignore # Intentional to raise an error if not defined

    def setUp(self) -> None:
        super().setUp()
        # Create the schema for our model
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(self.MODEL)

    def tearDown(self) -> None:
        super().tearDown()
        # Delete the schema for the model
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(self.MODEL)


class MockResponse(requests.Response):
    """Auxiliary class to mock a `requests.Response`."""

    def __init__(self, code: int, json_response: JSON_BASE = {}) -> None:
        self.status_code = code
        self.json_data = json_response

    def json(self, *args: Any, **kwargs: Any) -> JSON_BASE:
        return self.json_data

    @property
    def text(self) -> str:
        return str(self.json_data)

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400


def clear_colors(message: str) -> str:
    """Clear ANSI colors from a string."""
    # 7-bit C1 ANSI sequences
    ansi_escape = re.compile(
        r"""
        \x1B  # ESC
        (?:   # 7-bit C1 Fe (except CSI)
            [@-Z\\-_]
        |     # or [ for CSI, followed by a control sequence
            \[
            [0-?]*  # Parameter bytes
            [ -/]*  # Intermediate bytes
            [@-~]   # Final byte
        )
    """,
        re.VERBOSE,
    )
    return ansi_escape.sub("", message)
