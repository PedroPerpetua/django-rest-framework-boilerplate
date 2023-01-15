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


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer to obtain an user's profile."""
    class Meta:
        model = models.User
        fields = ("email",)
