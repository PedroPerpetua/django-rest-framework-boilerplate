from typing import Any
import requests


class MockResponse(requests.Response):
    """Auxiliary class to mock a `requests.Response`."""

    def __init__(self, code: int, json_response: Any) -> None:
        self.status_code = code
        self.json_data = json_response

    def json(self, *args: Any, **kwargs: Any) -> Any:
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
