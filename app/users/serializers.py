from typing import Any
from rest_framework import serializers
from users import models


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for creating users."""

    class Meta:
        model = models.User
        fields = ("id", "username", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data: Any) -> models.User:
        return models.User.objects.create_user(**validated_data)


class UserWhoamiSerializer(serializers.ModelSerializer):
    """Serializer for retrieving the current user's `USERNAME_FIELD` data (usually username or email)."""

    class Meta:
        model = models.User
        fields = (models.User.USERNAME_FIELD,)


class UserChangePasswordSerializer(serializers.ModelSerializer):
    """Serializer for change password requests."""

    password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = models.User
        fields = ("password", "new_password")


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer to handle user's details."""

    class Meta:
        model = models.User
        # Because more fields can be included in the user, instead exclude all that we know we don't want
        exclude = (
            "id",
            "created_at",
            "updated_at",
            "is_deleted",
            "is_staff",
            "is_active",
            "is_superuser",
            "password",
            "last_login",
            "groups",
            "user_permissions",
        )
