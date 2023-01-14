from typing import Any
from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from users import serializers


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

    def post(self, request: Request) -> Response:
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
        request.user.set_password(new_password)
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserLogoutView():
    """Endpoint for the user to log themselves out."""


class UserProfileView():
    """Endpoint to get a user's details."""
