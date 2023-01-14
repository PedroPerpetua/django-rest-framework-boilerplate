from typing import Any
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from users import models, serializers


class AuthenticatedRequest(Request):
    """Authenticated class to correctly type the user in requests."""
    user: models.User


class UserWhoamiView(APIView):
    """Endpoint to retrieve the email of the currently logged in user."""
    http_method_names = ["get"]
    permission_classes = (IsAuthenticated,)

    def get(self, request: AuthenticatedRequest) -> Response:
        return Response({"email": request.user.email}, status=status.HTTP_200_OK)


class UserRegisterView(generics.CreateAPIView):
    """Endpoint to register users."""
    serializer_class = serializers.UserRegisterSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Override the POST method to block registration if disabled."""
        registration_enabled: bool = settings.AUTH_USER_REGISTRATION_ENABLED
        if not registration_enabled:
            return Response(
                {"errcode": "REG_DISABLED", "error": "Registration is disabled."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().post(request, *args, **kwargs)


class UserChangePasswordView(APIView):
    """Endpoint to change a user's password."""
    http_method_names = ["post"]
    permission_classes = (IsAuthenticated,)

    def post(self, request: AuthenticatedRequest) -> Response:
        password = request.data.get("password", None)
        if password is None:
            return Response(
                {"errcode": "MISSING_ARG", "error": "'password' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        new_password = request.data.get("new_password", None)
        if new_password is None:
            return Response(
                {"errcode": "MISSING_ARG", "error": "'new_password' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not request.user.check_password(password):
            return Response(
                {"errcode": "WRONG_PASSWORD", "error": "The original password is wrong."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            validate_password(new_password)
        except ValidationError:
            return Response(
                {"errcode": "INVALID_PASSWORD", "error": "The new password is invalid."},
                status=status.HTTP_400_BAD_REQUEST
            )
        request.user.set_password(new_password)
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Endpoint to get a user's details."""
    serializer_class = serializers.UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self) -> AbstractBaseUser | AnonymousUser:
        return self.request.user
