from rest_framework.generics import GenericAPIView
from extensions.utilities.types import GenericViewMixin
from users.authentication import AuthenticatedRequest, IsAuthenticated, IsStaff
from users.models import User


class AuthenticatedUserMixin(GenericViewMixin):
    """Mixin to set that a view requires authentication, and type the request as an AuthenticatedRequest."""

    permission_classes = (IsAuthenticated,)
    request: AuthenticatedRequest


class AuthenticatedStaffMixin(AuthenticatedUserMixin):
    """
    Mixin to set that a view requires authentication by a staff user, and type the request as an AuthenticatedRequest.
    """

    permission_classes = (IsStaff,)


class TargetAuthenticatedUserMixin(AuthenticatedUserMixin):
    """Mixin for views that target the authenticated user."""

    def get_object(self: GenericAPIView) -> User:
        return self.request.user  # type: ignore # Return our user instead of an abstraction
