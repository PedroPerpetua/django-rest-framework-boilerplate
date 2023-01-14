from typing import Any
from django.conf import settings
from rest_framework import generics, status
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


class UserProfileView():
    """Endpoint to get a user's details."""


class UserChangePasswordView():
    """Endpoint to change a user's password."""
