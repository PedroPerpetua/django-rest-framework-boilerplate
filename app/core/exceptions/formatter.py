from dataclasses import asdict
from drf_standardized_errors.formatter import ExceptionFormatter as BaseExceptionFormatter
from drf_standardized_errors.types import ErrorResponse
from core.utilities.types import JSON


class ExceptionFormatter(BaseExceptionFormatter):
    def format_error_response(self, error_response: ErrorResponse) -> JSON:
        return {"errors": [asdict(err) for err in super().get_errors()]}
