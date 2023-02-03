from typing import Any
from django.contrib.auth.models import BaseUserManager
from core.utilities.types import GenericUser


class UserManager(BaseUserManager[GenericUser]):
    """Custom UserManager that uses our User model defined below."""

    def create_user(self, password: str, **fields: Any) -> GenericUser:
        """Create, save and return a new User."""
        user = self.model(password=password, **fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, password: str, **fields: Any) -> GenericUser:
        """Shortcut method to create a User with `is_staff` and `is_superuser` as `True`."""
        return self.create_user(password, is_staff=True, is_superuser=True, **fields)
