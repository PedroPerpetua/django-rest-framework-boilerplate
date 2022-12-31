from __future__ import annotations
from typing import Any, Iterable, Optional
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from core.extensions.models import BaseAbstractModel


class UserManager(BaseUserManager["User"]):
    """Custom UserManager that uses our User model defined below."""

    def create_user(self, email: str, password: str, **extra_fields: Any) -> User:
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

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None
    ) -> None:
        if self.email:
            # Use the UserManager normalize email function
            self.email = UserManager.normalize_email(self.email)
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return f"User ({self.id}) {self.email}"

    def __repr__(self) -> str:
        return f"User { {'id': self.id, 'email': self.email} }"
