from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated as BaseIsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView
from core.utilities.types import GenericViewMixin
from users.models import User


class AuthenticatedRequest(Request):
    """Authenticated class to correctly type the user in requests."""

    user: User


class IsAuthenticated(BaseIsAuthenticated):
    """Modify the IsAuthenticated permission to block inactive and deleted users."""
    def has_permission(self, request: AuthenticatedRequest, view: APIView) -> bool:  # type: ignore # Use our User
        return super().has_permission(request, view) and request.user.is_active and not request.user.is_deleted


class AuthenticatedUserMixin(GenericViewMixin):
    """Mixin to set that a view requires authentication, and type the request as an AuthenticatedRequest."""

    permission_classes = (IsAuthenticated,)
    request: AuthenticatedRequest


class TargetAuthenticatedUserMixin(AuthenticatedUserMixin):
    """Mixin for views that target the authenticated user."""

    def get_object(self: GenericAPIView) -> User:
        return self.request.user  # type: ignore # Return our user instead of an abstraction
