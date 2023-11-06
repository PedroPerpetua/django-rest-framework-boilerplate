from typing import TYPE_CHECKING, Any
from django.contrib.auth.models import BaseUserManager
from extensions.models.managers import SoftDeleteManager


if TYPE_CHECKING:
    from users.models import User
else:
    from django.db import models

    User = models.Model


class UserManager(SoftDeleteManager[User], BaseUserManager[User]):
    """Custom UserManager that uses our User model defined below."""

    def create_user(self, password: str, **fields: Any) -> User:
        """Create, save and return a new User."""
        user = self.model(**fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, password: str, **fields: Any) -> User:
        """Shortcut method to create a User with `is_staff` and `is_superuser` as `True`."""
        fields.update({"is_staff": True, "is_superuser": True})
        return self.create_user(password, **fields)
