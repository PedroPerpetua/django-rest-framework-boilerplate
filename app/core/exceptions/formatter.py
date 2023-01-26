from dataclasses import asdict
from drf_standardized_errors.formatter import ExceptionFormatter as BaseExceptionFormatter  # type: ignore
from drf_standardized_errors.types import ErrorResponse  # type: ignore
from core.utilities.types import JSON


"""
TODO: fix drf_standardized_errors types.
The module is currently missing it's `py.typed` file. An issue has been raised and the owner is on it. Once the issue
is fixed, the module should be updated and all `# type: ignore`s removed.
Issue: https://github.com/ghazi-git/drf-standardized-errors/issues/32
"""


class ExceptionFormatter(BaseExceptionFormatter):  # type: ignore
    def format_error_response(self, error_response: ErrorResponse) -> JSON:  # type: ignore
        return {"errors": [asdict(err) for err in super().get_errors()]}
