from typing import Any, Optional
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import exception_handler as default_exception_handler


def exception_handler(exc: Exception, context: Any) -> Optional[Response]:
    """
    Due to some funky logic on how authentication is handled in Django, our current configuration makes it so an
    AuthenticationFailed exception raises a 403 HTTP error instead of the expected 401 HTTP error. This exception
    handler fixes that.
    """
    # Call the default handler first
    response = default_exception_handler(exc, context)
    if response is not None and isinstance(exc, AuthenticationFailed):
        response.status_code = status.HTTP_401_UNAUTHORIZED
    return response
