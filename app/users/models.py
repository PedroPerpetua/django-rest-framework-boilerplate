from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from extensions.models import AbstractBaseModel
from extensions.models.mixins import SoftDeleteMixin
from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, SoftDeleteMixin, AbstractBaseModel):
    """
    The concrete user class that will be used in the database.

    By default, implements a `username` field, and `is_staff` and `is_active` status, alongside everything provided by
    the `BaseAbstractModel`.
    """

    username = models.CharField(unique=True, max_length=255)

    is_active = models.BooleanField(
        default=True, help_text="Designates the user as active.", verbose_name="active status"
    )
    is_staff = models.BooleanField(
        default=False, help_text="Designates this user as a staff member.", verbose_name="staff status"
    )

    USERNAME_FIELD = "username"
    objects = UserManager()

    class Meta(AbstractBaseModel.Meta): ...

    def __str__(self) -> str:
        return f"User ({self.id}) {self.get_username()}"
