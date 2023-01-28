import re
from typing import Any
import requests
from core.utilities.types import JSON_BASE


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


def clear_model_args(**kwargs: Any) -> dict[str, Any]:
    """Return a list of a model arguments with `None` values filtered out."""
    return {k: v for k, v in kwargs.items() if v is not None}


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
