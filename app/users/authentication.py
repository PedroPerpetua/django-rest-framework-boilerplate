from typing import Optional
from django.contrib.auth.backends import ModelBackend
from rest_framework.permissions import IsAuthenticated as BaseIsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView
from users.models import User


class AuthenticationBackend(ModelBackend):
    """Custom authentication backend that also checks for the `is_deleted` status."""

    def user_can_authenticate(self, user: Optional[User]) -> bool:  # type: ignore # Use our User
        not_deleted = not getattr(user, "is_deleted", False)
        return not_deleted and super().user_can_authenticate(user)


class AuthenticatedRequest(Request):
    """Authenticated class to correctly type the user in requests."""

    user: User


class IsAuthenticated(BaseIsAuthenticated):
    """Modify the IsAuthenticated permission to block inactive and deleted users."""

    def has_permission(self, request: AuthenticatedRequest, view: APIView) -> bool:  # type: ignore # Use our User
        return super().has_permission(request, view) and request.user.is_active and not request.user.is_deleted


class IsStaff(IsAuthenticated):
    """Extend the `IsAuthenticated` permission to only allow users with `is_staff == True`."""

    def has_permission(self, request: AuthenticatedRequest, view: APIView) -> bool:  # type: ignore # Use our User
        return super().has_permission(request, view) and request.user.is_staff
