import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Type, cast
from unittest import SkipTest
import requests
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.db.models import Model
from django.test import TestCase
from rest_framework.test import APITestCase as DRFAPITestCase
from extensions.utilities import uuid
from extensions.utilities.types import JSON


if TYPE_CHECKING:
    from rest_framework.response import _MonkeyPatchedResponse as Response

else:
    from rest_framework.response import Response


class APITestCase(DRFAPITestCase):  # pragma: no cover

    def assertResponseStatusCode(self, expected_status_code: int, response: Response) -> None:
        """
        Assert that the response's status code matches the expected one.

        This will raise an exception with the response's content in case of failure.

        This is equivalent to `self.assertEqual(expected_status_code, response.status_code, content)`.
        """
        try:
            content = response.json()
        except:
            content = str(response.content)
        self.assertEqual(expected_status_code, response.status_code, content)


class AbstractModelTestCase(TestCase):  # pragma: no cover
    """
    TestCase class to generate new models from an abstract at runtime.

    Usage: use this class as the test class, and set the class variable MODELS to a list of concrete models generated
    from the abstract class under test. For example, to test `MyAbstractModel`:

    ```py
    class MyAbstractClassTests(AbstractModelTestCase):

        class MyConcreteModel(MyAbstractModel):
            # Any additional settings
            ...

        MODELS = [MyConcreteModel]

        def my_test(self) -> None:
            # Use self.MyConcreteModel
            ...
    ```

    Adapted from: https://michael.mior.ca/blog/unit-testing-django-model-mixins/
    """

    MODELS: list[Type[Model]] = []

    @classmethod
    def setUpClass(cls) -> None:
        if len(cls.MODELS) == 0:
            raise SkipTest(
                "AbstractModelTestCase class used with no MODELS. Did you forget to include your abstract models in "
                "the class variable?",
            )
        # Create the schemas for all models
        with connection.schema_editor() as schema_editor:
            for model in cls.MODELS:
                schema_editor.create_model(model)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        # Delete the created schemas
        with connection.schema_editor() as schema_editor:
            for model in cls.MODELS:
                schema_editor.delete_model(model)


class MockResponse(requests.Response):
    """Auxiliary class to mock a `requests.Response`."""

    def __init__(self, code: int, json_response: JSON = {}) -> None:
        self.status_code = code
        self.json_data = json_response

    def json(self, *args: Any, **kwargs: Any) -> JSON:
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
    def from_file_path(file_path: str | Path) -> "SampleFile":
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
