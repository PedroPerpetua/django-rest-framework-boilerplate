from typing import Any
from django.conf import settings
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from core.utilities.types import GenericViewMixin
from users import models, serializers


class AuthenticatedRequest(Request):
    """Authenticated class to correctly type the user in requests."""

    user: models.User


class TargetAuthenticatedUserMixin(GenericViewMixin):
    """Mixin for views that target the authenticated user."""

    permission_classes = (IsAuthenticated,)
    request: AuthenticatedRequest

    def get_object(self: generics.GenericAPIView) -> models.User:
        return self.request.user  # type: ignore # Return our user instead of an abstraction


class UserRegisterView(generics.CreateAPIView):
    """Endpoint to register users."""

    serializer_class = serializers.UserRegisterSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Override the POST method to block registration if disabled."""
        registration_enabled: bool = settings.AUTH_USER_REGISTRATION_ENABLED
        if not registration_enabled:
            raise PermissionDenied("Registration is disabled.")
        return super().post(request, *args, **kwargs)


class UserWhoamiView(TargetAuthenticatedUserMixin, generics.RetrieveAPIView):
    """Endpoint to retrieve the email of the currently logged in user."""

    serializer_class = serializers.UserWhoamiSerializer


class UserProfileView(TargetAuthenticatedUserMixin, generics.RetrieveUpdateAPIView):
    """Endpoint to get a user's details."""

    serializer_class = serializers.UserProfileSerializer


class UserChangePasswordView(TargetAuthenticatedUserMixin, generics.UpdateAPIView):
    """Endpoint to change an user's password."""

    serializer_class = serializers.UserChangePasswordSerializer

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not user.check_password(serializer.data.get("password")):
            raise PermissionDenied("Wrong Password")
        user.set_password(serializer.data.get("new_password"))
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
