from typing import TYPE_CHECKING, Iterable, Optional
from django.contrib.auth.models import AbstractBaseUser as DjangoAbstractBaseUser
from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models
from django.utils.functional import classproperty
from core.extensions.models import BaseAbstractModel
from core.utilities import empty


class BaseAbstractUser(PermissionsMixin, DjangoAbstractBaseUser, BaseAbstractModel):
    """
    Custom BaseAbstractUser model that should serve as a base for any custom User models.

    At least one of `UserEmailMixin` or `UserUsernameMixin` should be added to the concrete User model (both can be
    added simultaneously too), and the following variables have to be defined:
    - `USERNAME_FIELD`: either "username" or "email".
    - `objects`: a UserManager capable of handling the concrete class.
    """

    USERNAME_FIELD: str = None  # type: ignore # Intentional to raise an error if not defined
    objects: BaseUserManager = None  # type: ignore # Intentional to raise an error if not defined

    class Meta(BaseAbstractModel.Meta):
        abstract = True

    is_staff = models.BooleanField(
        default=False, help_text="Designates this user as a staff member.", verbose_name="staff status"
    )
    is_active = models.BooleanField(
        default=True, help_text="Designates the user as active.", verbose_name="active status"
    )

    # Fix the last_login help text
    last_login = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Last login datetime. Updated when the UserLoginView is called.",
        verbose_name="last_login",
    )

    """
    Other fields not included but acquired from the DjangoAbstractBaseUser:
    - password: string[128] -> encrypted password.
    - is_superuser: boolean -> the user is a Django Superuser.
    - groups: MTM[auth.group] -> permission groups the user belongs to.
    - user_permissions: MTM[auth.permission] -> specific permissions applied to the user.
    """

    @classmethod
    def set_required_field(cls, fields: list[str], field_name: str, should_add: bool) -> list[str]:
        """
        Generate a list of fields making sure the passed `field_name` is only included if and only if
        `should_add = True`
        """
        if field_name in fields:
            fields.remove(field_name)
        if should_add:
            fields += [field_name]
        return fields


"""
Because of some weird results with `related_names` (inheriting from the PermissionsMixin multiple times) and having
issues with needing to override the same field multiple times when we do inheritance (specifically with the
`last_login` field) we opt to inherit from the basic `models.model` on runtime, but for typechecking purposes, we
still use the BaseAbstractUser (which will always be the "main" class when using these mixins).
"""
if TYPE_CHECKING:
    BaseUserMixin = BaseAbstractUser
else:
    BaseUserMixin = models.Model


class UserEmailMixin(BaseUserMixin):
    """
    Mixin to add an email field to the custom concrete User class.

    In order to use this as the username field, set `USERNAME_FIELD = "email"`.

    If this is not the username field, but still a required field, set `REQUIRE_EMAIL = True` (defaults to `False`).
    """

    USERNAME_FIELD: str  # Will be inherited from Permissions Mixin

    class Meta:
        abstract = True

    REQUIRE_EMAIL = False
    email = models.EmailField(max_length=255, unique=True)

    @classproperty
    def REQUIRED_FIELDS(cls) -> list[str]:  # type: ignore # mypy bug: https://github.com/python/mypy/issues/4125
        should_add = cls.REQUIRE_EMAIL and cls.USERNAME_FIELD != "email"
        return BaseAbstractUser.set_required_field(super().REQUIRED_FIELDS, "email", should_add)

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        if self.REQUIRE_EMAIL or self.USERNAME_FIELD == "email":
            if empty(self.email):
                raise ValidationError("Email cannot be empty.")
            try:
                validate_email(self.email)
            except ValidationError as ve:
                raise ValidationError("Email is invalid.") from ve
        self.email = BaseUserManager.normalize_email(self.email.strip())
        return super().save(force_insert, force_update, using, update_fields)


class UserUsernameMixin(BaseUserMixin):
    """
    Mixin to add a username field to the custom concrete User class.

    In order to use this as the username field, set `USERNAME_FIELD = "username"`.

    If this is not the username field, but still a required field, set `REQUIRE_USERNAME = True` (defaults to
    `False`).
    """

    USERNAME_FIELD: str  # Will be inherited from Permissions Mixin

    class Meta:
        abstract = True

    REQUIRE_USERNAME = False
    username = models.CharField(max_length=255, unique=True)

    @classproperty
    def REQUIRED_FIELDS(cls) -> list[str]:  # type: ignore # mypy bug: https://github.com/python/mypy/issues/4125
        should_add = cls.REQUIRE_USERNAME and cls.USERNAME_FIELD != "username"
        return BaseAbstractUser.set_required_field(super().REQUIRED_FIELDS, "username", should_add)

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        if empty(self.username) and (self.REQUIRE_USERNAME or self.USERNAME_FIELD == "username"):
            raise ValidationError("Username cannot be empty.")
        self.username = self.username.strip()
        return super().save(force_insert, force_update, using, update_fields)
