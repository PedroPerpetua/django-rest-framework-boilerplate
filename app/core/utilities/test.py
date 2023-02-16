from __future__ import annotations
import re
from pathlib import Path
from typing import Any, Optional, Type, cast
import requests
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.db.models import Model
from django.test import TestCase
from core.utilities import uuid
from core.utilities.types import JSON_BASE


class AbstractModelTestCase(TestCase):
    """
    Test case class to generate a new model from an abstract at runtime.

    Usage: use this class as the test class, and set the class variable MODEL to the concrete model you generated with
    the abstract class. For example, to test `MyAbstractModel`:

    ```py
    class MyAbstractClassTests(AbstractModelTestCase):

        class MyConcreteModel(MyAbstractModel):
            # Any adittional settings
            ...

        MODEL = MyConcreteModel

        def my_test(self) -> None:
            # Use self.MyConcreteModel or self.MODEL here
            ...
    ```

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


class SampleFile(SimpleUploadedFile):
    """
    Wrapper for SimpleUploadedFile to generate sample files for testing.

    This class subclasses SimpleUploadedFile and supports a filename (randomly generated if not given) and two
    convenience properties, `bytes` and `content`, to get the content as bytes and string respectively.

    Can be initialized with content from a string, bytes, or mirror a real file with the `from_file_path` method.
    """

    def __init__(self, name: Optional[str] = None, content: Optional[str | bytes] = None) -> None:
        if name is None:
            name = uuid()
        if isinstance(content, str):
            content = content.encode()
        super().__init__(name, content)

    @property
    def bytes(self) -> bytes:
        """Returns the contents of the file as bytes."""
        assert self.file is not None
        self.file.seek(0)
        return cast(bytes, self.file.read())

    @property
    def content(self) -> str:
        """Returns the contents of the file as a string."""
        return self.bytes.decode()

    @staticmethod
    def from_file_path(file_path: str | Path) -> SampleFile:
        """Generates a SampleFile from a real file, having the same contents."""
        if isinstance(file_path, str):
            file_path = Path(file_path)
        with open(file_path, "rb") as file:
            return SampleFile(file_path.name, file.read())


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
