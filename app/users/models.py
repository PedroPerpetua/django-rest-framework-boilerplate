from __future__ import annotations
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from core.extensions.models import BaseAbstractModel


class UserManager(BaseUserManager):
    """Custom UserManager that uses our User model defined below."""

    def create_user(self, email, password, **extra_fields) -> User:
        """Create, save and return a new User"""
        user = self.model(email=email, password=password, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class User(BaseAbstractModel, AbstractBaseUser, PermissionsMixin):
    """Custom User model."""
    email = models.EmailField(max_length=255, unique=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'


    def __str__(self) -> str:
        return f"User ({self.id}) {self.email}"

    def __repr__(self) -> str:
        return f"User { {'id': self.id, 'email': self.email} }"
