from typing import Any
from constance import config  # type: ignore[import-untyped]
from drf_standardized_errors.openapi import AutoSchema as BaseAutoSchema


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


def post_processing_hook_apply_config(result: dict[str, Any], *args: Any, **kwargs: Any) -> dict[str, Any]:
    """
    Apply the constance configs to the schema definition. We do this at a post_processing_hook level so we have access
    to the configs.
    """
    # Apply the constance configs
    result["info"]["title"] = config.OPENAPI_TITLE
    result["info"]["description"] = config.OPENAPI_DESCRIPTION
    result["info"]["version"] = config.OPENAPI_VERSION
    return result
