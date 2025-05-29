import json
from typing import Any, Iterable, Optional
from uuid import uuid4
from django.conf import settings
from django.db import models
from django.db.models.fields.files import FieldFile
from django.utils.translation import gettext_lazy as _


class UUIDPrimaryKeyMixin(models.Model):
    """Mixin to use a UUID field as the primary key field."""

    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)

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

    @classmethod
    def _get_short_repr_data(cls, obj: models.Model) -> dict[str, Any]:
        """Return the simplest representation for a model - it's model class name and it's `pk`."""
        return {"model": obj.__class__.__name__, "pk": obj.pk}

    @classmethod
    def _get_iterable_repr_data(
        cls,
        items: Iterable[models.Model],
        ignore_models: Optional[list[models.Model]] = None,
    ) -> list[dict[str, Any]]:
        """
        Return a list of model instances's representation; usually used to serialize many related managers.

        This method can receive an `ignore_models` list that will pass down to the model representations, as well as
        serialize any item that's in the `ignore_models` with the short representation instead.
        """
        if ignore_models is None:  # pragma: no cover
            ignore_models = []
        retval: list[dict[str, Any]] = []
        for item in items:
            if item in ignore_models:
                retval.append(cls._get_short_repr_data(item))
            else:
                retval.append(cls._get_repr_data(item, ignore_models))
        return retval

    @classmethod
    def _get_repr_data(cls, obj: models.Model, ignore_models: Optional[list[models.Model]] = None) -> dict[str, Any]:
        """
        Iterate over all the instance's fields and return them as a a dictionary.

        Other model instances found while iterating are also serialized with this method.

        This method can receive an `ignore_models` list that will pass down to the model representations, as well as
        serialize any item that's in the `ignore_models` with the short representation instead. This is used mostly to
        avoid infinite loops.

        **Note:** if DEBUG is turned off, this will ALWAYS return the short representation (model name and `pk` only)
        in order to prevent performance issues in models with relationships.
        """
        if not settings.DEBUG:
            return cls._get_short_repr_data(obj)
        if ignore_models is None:  # pragma: no cover
            ignore_models = []
        data = cls._get_short_repr_data(obj)
        try:
            for field in obj._meta.get_fields():
                try:
                    value = getattr(obj, field.name)
                except AttributeError:
                    # Field is in the meta but doesn't have a value
                    continue
                if isinstance(field, (models.ManyToOneRel, models.OneToOneRel)):
                    # Field is a "direct" relationship (can be one or more model instances)
                    qs = getattr(obj, field.get_accessor_name(), obj.__class__._default_manager.none())
                    if isinstance(qs, models.Model):
                        value = qs
                    else:
                        value = cls._get_iterable_repr_data(qs.iterator(), ignore_models + [obj])
                elif isinstance(field, (models.ManyToManyField, models.ManyToManyRel)):
                    # Field is a M2M relationship
                    value = cls._get_iterable_repr_data(value.iterator(), ignore_models + [obj])
                elif hasattr(obj, f"get_{field.name}_display"):
                    # Field is a choice field; use the choice value
                    value = getattr(obj, f"get_{field.name}_display")()

                if isinstance(value, models.Model):
                    # Serialize models with the repr method
                    if value in ignore_models:
                        data.update({field.name: cls._get_short_repr_data(value)})
                    else:
                        data.update({field.name: cls._get_repr_data(value, ignore_models + [obj])})
                elif isinstance(value, FieldFile):
                    # Serialize files by presenting the path
                    data.update({field.name: value.path})
                else:
                    data.update({field.name: value})
            return data
        except RecursionError:
            # If at any point we hit a recursion error (some loop we didn't account for), return short representation
            return cls._get_short_repr_data(obj)

    def __repr__(self) -> str:
        """
        Representation method that adds the model and al fields to a dictionary-like string. If the data can be JSON
        encoded, it will be; otherwise we just run it through Python's `str`.
        """
        data = self._get_repr_data(self)
        try:
            return json.dumps(data)
        except TypeError:
            return str(data)
