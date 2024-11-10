from typing import Optional
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import IsAuthenticated as BaseIsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView
from users.models import User


class AuthenticationBackend(ModelBackend):
    """Custom authentication backend that also checks for the `is_deleted` status."""

    def user_can_authenticate(self, user: Optional[User | AnonymousUser]) -> bool:
        """Override this method so that we can check for the `is_deleted` status."""
        if not user:  # pragma: no cover
            return False
        is_deleted = getattr(user, "is_deleted", False)
        if is_deleted:
            return False
        return super().user_can_authenticate(user)


class IsAuthenticated(BaseIsAuthenticated):
    """Modify the IsAuthenticated permission to block inactive and deleted users."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return super().has_permission(request, view) and request.user.is_active and not request.user.is_deleted


class IsStaff(IsAuthenticated):
    """Extend the `IsAuthenticated` permission to only allow users with `is_staff == True`."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return super().has_permission(request, view) and request.user.is_staff
