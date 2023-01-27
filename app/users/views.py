from typing import Any
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt import views as jwt_views  # type: ignore # No stubs available
from users import serializers
from users.mixins import TargetAuthenticatedUserMixin


@extend_schema(tags=["User Authentication"])
@extend_schema(description="Endpoint to register users.")
class UserRegisterView(generics.CreateAPIView):
    """Endpoint to register users."""

    serializer_class = serializers.UserRegisterSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Override the POST method to block registration if disabled."""
        registration_enabled: bool = settings.AUTH_USER_REGISTRATION_ENABLED
        if not registration_enabled:
            raise PermissionDenied("Registration is disabled.")
        return super().post(request, *args, **kwargs)


@extend_schema(tags=["User Authentication"])
class UserLoginView(jwt_views.TokenObtainPairView):  # type: ignore # missing stubs
    """Endpoint to login a user and obtain a pair of `(access_token, refresh_token)`."""

    ...


@extend_schema(tags=["User Authentication"])
class UserLoginRefreshView(jwt_views.TokenRefreshView):  # type: ignore # missing stubs
    """Endpoint to refresh the user's `access_token` and `refresh_token`, from a valid `refresh_token`."""

    ...


@extend_schema(tags=["User Authentication"])
class UserLogoutView(jwt_views.TokenBlacklistView):  # type: ignore # missing stubs
    """
    Endpoint to logout the user, by blacklisting it's `access_token` and `refresh_token`, from a valid
    `refresh_token`.
    """

    ...


@extend_schema(tags=["Users"])
class UserWhoamiView(TargetAuthenticatedUserMixin, generics.RetrieveAPIView):
    """Endpoint to retrieve the email of the currently logged in user."""

    serializer_class = serializers.UserWhoamiSerializer


@extend_schema(tags=["Users"])
class UserProfileView(TargetAuthenticatedUserMixin, generics.RetrieveUpdateAPIView):
    """Endpoint to retrieve and update a user's details."""

    serializer_class = serializers.UserProfileSerializer

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Endpoint to retrieve a user's details."""
        return super().get(request, *args, **kwargs)

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Endpoint to partially update a user's details."""
        return super().patch(request, *args, **kwargs)

    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Endpoint to fully override a user's details."""
        return super().put(request, *args, **kwargs)


@extend_schema(tags=["Users"])
@extend_schema(description="Endpoint to change a user's password.")
class UserChangePasswordView(TargetAuthenticatedUserMixin, generics.UpdateAPIView):
    """
    Endpoint to change a user's password.

    Even though the generic UpdateAPIView uses PUT/PATCH, an update-password request is recommended to be made trough
    POST, so we change the methods here and implement the `post` method.
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
