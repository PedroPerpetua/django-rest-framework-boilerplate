from typing import Iterable, Optional
from django.contrib.auth.models import AbstractBaseUser as DjangoAbstractBaseUser
from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models
from django.utils.functional import classproperty
from core.extensions.models import BaseAbstractModel
from core.utilities import empty


class BaseAbstractUser(BaseAbstractModel, DjangoAbstractBaseUser, PermissionsMixin):
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
    """
    Other fields not included but acquired from the DjangoAbstractBaseUser:
    - password: string[128] -> encrypted password.
    - last_login: DateTime -> user's last login; to be updated make sure simplejwt has the setting as true.
        - NOTE: this field's help text is patched bellow
    - is_superuser: boolean -> the user is a Django Superuser.
    - groups: MTM[auth.group] -> permission groups the user belongs to.
    - user_permissions: MTM[auth.permission] -> specific permissions applied to the user.
    """

    @classmethod
    def append_required_field(cls, fields: list[str], field_name: str) -> None:
        if field_name not in fields and cls.USERNAME_FIELD != field_name:
            fields += [field_name]


BaseAbstractUser._meta.get_field(
    "last_login"
).help_text = "Last login datetime. Updated when the UserLoginView is called."


class UserEmailMixin(DjangoAbstractBaseUser):
    """
    Mixin to add an email field to the custom concrete User class.

    In order to use this as the username field, set `USERNAME_FIELD = "email"`.

    If this is not the username field, but still a required field, set `REQUIRE_EMAIL = True` (defaults to `False`).

    We don't subclass BaseAbstractUser because there can be some weird results with `related_names` (inheriting from
    the PermissionsMixin multiple times).
    """

    USERNAME_FIELD: str  # Will be inherited from Permissions Mixin

    class Meta:
        abstract = True

    REQUIRE_EMAIL = False
    email = models.EmailField(max_length=255, unique=True, blank=REQUIRE_EMAIL, null=REQUIRE_EMAIL)

    @classproperty
    def REQUIRED_FIELDS(cls) -> list[str]:  # type: ignore # mypy bug: https://github.com/python/mypy/issues/4125
        fields = super().REQUIRED_FIELDS
        if cls.REQUIRE_EMAIL:
            BaseAbstractUser.append_required_field(fields, "email")
        return fields

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


class UserUsernameMixin(DjangoAbstractBaseUser):
    """
    Mixin to add a username field to the custom concrete User class.

    In order to use this as the username field, set `USERNAME_FIELD = "username"`.

    If this is not the username field, but still a required field, set `REQUIRE_USERNAME = True` (defaults to
    `False`).

    We don't subclass BaseAbstractUser because there can be some weird results with `related_names` (inheriting from
    the PermissionsMixin multiple times).
    """

    USERNAME_FIELD: str  # Will be inherited from Permissions Mixin

    class Meta:
        abstract = True

    REQUIRE_USERNAME = False
    username = models.CharField(max_length=255, unique=True, blank=REQUIRE_USERNAME, null=REQUIRE_USERNAME)

    @classproperty
    def REQUIRED_FIELDS(cls) -> list[str]:  # type: ignore # mypy bug: https://github.com/python/mypy/issues/4125
        fields = super().REQUIRED_FIELDS
        if cls.REQUIRE_USERNAME:
            BaseAbstractUser.append_required_field(fields, "username")
        return fields

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
