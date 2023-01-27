from typing import Any
from rest_framework import serializers
from users import models


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for creating users."""

    class Meta:
        model = models.User
        fields = ("email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data: Any) -> models.User:
        return models.User.objects.create_user(**validated_data)


class UserWhoamiSerializer(serializers.ModelSerializer):
    """Serializer for retrieving the current user's email."""

    class Meta:
        model = models.User
        fields = ("email",)


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
        fields = ("email",)
