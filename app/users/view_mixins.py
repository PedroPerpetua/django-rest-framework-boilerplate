from typing import cast
from rest_framework.generics import GenericAPIView
from extensions.utilities.types import GenericViewMixin
from users.authentication import IsAuthenticated, IsStaff
from users.models import User


class AuthenticatedUserMixin(GenericViewMixin):
    """Mixin to set that a view requires authentication, and type the request as an AuthenticatedRequest."""

    permission_classes = (IsAuthenticated,)


class AuthenticatedStaffMixin(AuthenticatedUserMixin):
    """
    Mixin to set that a view requires authentication by a staff user, and type the request as an AuthenticatedRequest.
    """

    permission_classes = (IsStaff,)


class TargetAuthenticatedUserMixin(AuthenticatedUserMixin):
    """Mixin for views that target the authenticated user."""

    def get_object(self: GenericAPIView) -> User:
        return cast(User, self.request.user)
