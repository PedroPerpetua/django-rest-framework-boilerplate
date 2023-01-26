from typing import Any
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from core.utilities.types import GenericViewMixin
from users import models, serializers


class AuthenticatedRequest(Request):
    """Authenticated class to correctly type the user in requests."""

    user: models.User


class AuthenticatedUserMixin(GenericViewMixin):
    """Mixin to set that a view requires authentication, and type the request as an AuthenticatedRequest."""

    permission_classes = (IsAuthenticated,)
    request: AuthenticatedRequest


class TargetAuthenticatedUserMixin(AuthenticatedUserMixin):
    """Mixin for views that target the authenticated user."""

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
    """
    Endpoint to change an user's password.

    Even though the generic UpdateAPIView uses PUT/PATCH, an update-password request should be made trough POST, so we
    change the class here.
    """

    http_method_names = ["post"]
    serializer_class = serializers.UserChangePasswordSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self.update(request, *args, **kwargs)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not user.check_password(serializer.data.get("password")):
            raise PermissionDenied("Wrong Password")
        new_password = serializer.data.get("new_password")
        try:
            validate_password(new_password)
        except ValidationError as ve:
            raise DRFValidationError(ve.messages)
        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
