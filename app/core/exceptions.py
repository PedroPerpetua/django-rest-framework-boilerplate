from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import as_serializer_error
from drf_standardized_errors.handler import ExceptionHandler as BaseExceptionHandler
from drf_standardized_errors.openapi import AutoSchema as BaseAutoSchema


class ExceptionHandler(BaseExceptionHandler):
    """Custom ExceptionHandler for drf_standardized_errors that will properly handle Django ValidationErrors."""

    def convert_known_exceptions(self, exc: Exception) -> Exception:
        """
        Override this method so that all Django ValidationErrors are converted to DRF ValidationErrors before being
        processed.
        """
        if isinstance(exc, DjangoValidationError):
            return ValidationError(as_serializer_error(exc))
        return super().convert_known_exceptions(exc)


class AutoSchema(BaseAutoSchema):  # pragma: no cover
    """
    Custom AutoSchema for drf_spectacular so that the drf_standardized_errors are not automatically added to GET and
    DELETE requests.
    """

    def _should_add_error_response(self, responses: dict, status_code: str) -> bool:
        """Override this method so that GET and DELETE requests are skipped."""
        if self.method in ("GET", "DELETE"):
            return False
        return super()._should_add_error_response(responses, status_code)
