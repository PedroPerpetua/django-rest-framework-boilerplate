from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from extensions.models import AbstractBaseModel
from extensions.models.mixins import SoftDeleteMixin
from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, SoftDeleteMixin, AbstractBaseModel):
    """
    The concrete user class that will be used in the database.

    By default, implements a `username` field, and `is_staff` and `is_active` status, alongside everything provided by
    the `BaseAbstractModel`.
    """

    username = models.CharField(max_length=255, unique=True, verbose_name=_("username"))
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("active status"),
        help_text=_("Designates the user as active."),
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_("staff status"),
        help_text=_("Designates this user as a staff member."),
    )

    objects = UserManager()
    USERNAME_FIELD = "username"

    class Meta(AbstractBaseModel.Meta):
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self) -> str:
        return self.get_username()
