from __future__ import annotations
from typing import Any, Iterable, Optional
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import models
from core.extensions.models import BaseAbstractModel


class UserManager(BaseUserManager["User"]):
    """Custom UserManager that uses our User model defined below."""

    def create_user(self, email: str, password: str, **extra_fields: Any) -> User:
        """Create, save and return a new User."""
        user = self.model(email=email, **extra_fields)
        validate_password(password, user=user)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email: str, password: str, **extra_fields: Any) -> User:
        """Shortcut method to create a User with `is_staff` and `is_superuser` as `True`."""
        return self.create_user(email, password, is_staff=True, is_superuser=True, **extra_fields)


class User(BaseAbstractModel, AbstractBaseUser, PermissionsMixin):
    """Custom User model."""

    email = models.EmailField(max_length=255, unique=True)
    is_staff = models.BooleanField(
        default=False, help_text="Designates this user as a staff member.", verbose_name="staff status"
    )
    is_active = models.BooleanField(
        default=True, help_text="Designates the user as active.", verbose_name="active status"
    )
    """
    Other fields not included but acquired from the AbstractBaseUser:
    - password: string[128] -> encrypted password.
    - last_login: DateTime -> user's last login; to be updated make sure simplejwt has the setting as true.
        - NOTE: this field's help text is patched bellow
    - is_superuser: boolean -> the user is a Django Superuser.
    - groups: MTM[auth.group] -> permission groups the user belongs to.
    - user_permissions: MTM[auth.permission] -> specific permissions applied to the user.
    """

    objects = UserManager()
    USERNAME_FIELD = "email"

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        if self.email is None:
            raise ValidationError("Email cannot be empty.")
        stripped = self.email.strip()
        if len(stripped) == 0:
            raise ValidationError("Email cannot be empty.")
        # Use the UserManager normalize email function
        self.email = UserManager.normalize_email(stripped)
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return f"User ({self.id}) {self.email}"


# Patch the last_login field's help text.
User._meta.get_field("last_login").help_text = "Last login datetime. Updated when the TokenObtainPairView is called."
