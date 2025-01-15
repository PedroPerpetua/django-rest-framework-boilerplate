from uuid import uuid4
from django.db import models
from django.utils.translation import gettext_lazy as _


class UUIDPrimaryKeyMixin(models.Model):
    """Mixin to use a UUID field as the primary key field."""

    id = models.UUIDField(primary_key=True, unique=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class CreatedAtMixin(models.Model):
    """Mixin to add a `created_at` DateTimeField that sets the creation time."""

    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("created at"),
        help_text=_("Object creation datetime."),
    )

    class Meta:
        abstract = True


class UpdatedAtMixin(models.Model):
    """Mixin to add an `updated_at` DateTimeField that sets the creation time."""

    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name=_("updated at"),
        help_text=_("Last updated datetime."),
    )

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """
    Mixin to allow for soft deletion of the objects.
    This mixin sets a custom object manager to take into consideration soft-deleted instances, by filtering them out
    of the querysets.

    To further make use of this mixin, the SoftDeleteManager can be used on the respective models.
    """

    is_deleted = models.BooleanField(
        default=False,
        verbose_name=_("deleted status"),
        help_text=_("Designates this object as soft deleted."),
    )

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        """Soft delete this instance by marking `is_deleted` as `True`."""
        self.is_deleted = True
        self.save()


class ExtendedReprMixin(models.Model):
    """Mixin to add a more detailed `repr` method that will present all fields in a dictionary-like fashion."""

    class Meta:
        abstract = True

    def __repr__(self) -> str:
        """Representation method that adds the model and al fields to a dictionary-like."""
        data = {"model": self.__class__.__name__}
        for field in self._meta.get_fields():
            try:
                obj = getattr(self, field.name)
                if isinstance(field, models.OneToOneRel):
                    # Prevent infinite recursion
                    data.update({field.name: f"{obj.__class__.__name__} ({obj.pk})"})
                else:
                    data.update({field.name: obj})
            except AttributeError:
                # Field is in the meta but for some reason doesn't exist
                continue
        return str(data)
