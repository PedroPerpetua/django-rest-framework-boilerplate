from rest_framework.generics import GenericAPIView
from core.utilities.types import GenericViewMixin
from users.authentication import AuthenticatedRequest, IsAuthenticated
from users.models import User


class AuthenticatedUserMixin(GenericViewMixin):
    """Mixin to set that a view requires authentication, and type the request as an AuthenticatedRequest."""

    permission_classes = (IsAuthenticated,)
    request: AuthenticatedRequest


class TargetAuthenticatedUserMixin(AuthenticatedUserMixin):  # type: ignore
    """Mixin for views that target the authenticated user."""

    def get_object(self: GenericAPIView) -> User:
        return self.request.user  # type: ignore # Return our user instead of an abstraction
