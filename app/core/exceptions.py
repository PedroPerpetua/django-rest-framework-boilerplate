from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import as_serializer_error
from drf_standardized_errors.handler import ExceptionHandler as BaseExceptionHandler


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
