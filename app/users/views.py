from typing import Any
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework_simplejwt import views as jwt_views
from users import serializers
from users.view_mixins import TargetAuthenticatedUserMixin


@extend_schema(tags=["User Authentication"])
class UserRegisterView(generics.CreateAPIView):
    """Endpoint to register users."""

    serializer_class = serializers.UserRegisterSerializer

    @extend_schema(operation_id="users_register")
    @extend_schema(summary="Register user")
    @extend_schema(description="Endpoint to register users.")
    @extend_schema(
        responses={
            # Registration disabled
            403: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "type": {"enum": ["client_error"]},
                        "errors": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "code": {"enum": [PermissionDenied.default_code]},
                                    "detail": {"enum": ["Registration is disabled."]},
                                    "attr": {"enum": [None]},
                                },
                                "required": ["code", "detail", "attr"],
                            },
                        },
                    },
                    "required": ["type", "errors"],
                },
                description="Registration is disabled",
            )
        }
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Override the POST method to block registration if disabled."""
        registration_enabled: bool = settings.AUTH_USER_REGISTRATION_ENABLED
        if not registration_enabled:
            raise PermissionDenied("Registration is disabled.")
        return super().post(request, *args, **kwargs)


@extend_schema(tags=["User Authentication"])
@extend_schema_view(
    post=extend_schema(
        operation_id="users_login",
        summary="Login user",
        description="Endpoint to login a user and obtain a pair of `(access_token, refresh_token)`.",
    )
)
class UserLoginView(jwt_views.TokenObtainPairView): ...


@extend_schema(tags=["User Authentication"])
@extend_schema_view(
    post=extend_schema(
        operation_id="users_login_refresh",
        summary="Refresh access token",
        description="Endpoint to refresh the user's `access_token` and `refresh_token`, from a valid `refresh_token`.\n\nThis will also return a new refresh token and invalidate the old one.",
    )
)
class UserLoginRefreshView(jwt_views.TokenRefreshView): ...


@extend_schema(tags=["User Authentication"])
@extend_schema_view(
    post=extend_schema(
        operation_id="users_logout",
        summary="Logout user",
        description="Endpoint to logout the user, by blacklisting it's `access_token` and `refresh_token`, from a valid `refresh_token`.",
    )
)
class UserLogoutView(jwt_views.TokenBlacklistView): ...


@extend_schema(tags=["Users"])
@extend_schema_view(
    get=extend_schema(
        operation_id="users_whoami",
        summary="Get current user",
        description="Endpoint to retrieve the current logged in user.",
    )
)
class UserWhoamiView(TargetAuthenticatedUserMixin, generics.RetrieveAPIView):
    """Endpoint to retrieve the `USERNAME_FIELD` (usually `username` or `email`) of the currently logged in user."""

    serializer_class = serializers.UserWhoamiSerializer


@extend_schema(tags=["Users"])
@extend_schema_view(
    get=extend_schema(summary="Get user details", description="Endpoint to retrieve the current user's details."),
    put=extend_schema(
        summary="Update user details", description="Endpoint to partially update the current user's details."
    ),
    patch=extend_schema(
        summary="Patch user details", description="Endpoint to fully override the current user's details."
    ),
)
class UserProfileView(TargetAuthenticatedUserMixin, generics.RetrieveUpdateAPIView):
    """Endpoint to retrieve and update a user's details."""

    serializer_class = serializers.UserProfileSerializer


@extend_schema(tags=["Users"])
class UserChangePasswordView(TargetAuthenticatedUserMixin, generics.UpdateAPIView):
    """
    Endpoint to change a user's password.

    Even though the generic UpdateAPIView uses PUT/PATCH, an update-password request is recommended to be made trough
    POST, so we change the methods here and implement the `post` method.
    """

    http_method_names = ["post"]
    serializer_class = serializers.UserChangePasswordSerializer

    @extend_schema(operation_id="users_change_password")
    @extend_schema(summary="Change user's password")
    @extend_schema(description="Endpoint to change a user's password.")
    @extend_schema(
        responses={
            # Wrong "old" password
            401: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "type": {"enum": ["client_error"]},
                        "errors": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "code": {"enum": [AuthenticationFailed.default_code]},
                                    "detail": {"enum": ["Wrong password."]},
                                    "attr": {"enum": [None]},
                                },
                                "required": ["code", "detail", "attr"],
                            },
                        },
                    },
                    "required": ["type", "errors"],
                },
                description="Wrong password",
            )
        }
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self.update(request, *args, **kwargs)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not user.check_password(serializer.data.get("password")):
            raise AuthenticationFailed("Wrong password.")
        new_password = serializer.data.get("new_password")
        try:
            validate_password(new_password)
        except ValidationError as ve:
            raise DRFValidationError(ve.messages)
        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
