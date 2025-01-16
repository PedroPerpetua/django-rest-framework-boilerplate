from typing import Any
from django.db.models import Model
from extensions.models import mixins


class AbstractBaseModel(
    mixins.UUIDPrimaryKeyMixin,
    mixins.CreatedAtMixin,
    mixins.UpdatedAtMixin,
    mixins.ExtendedReprMixin,
    Model,
):
    """
    Abstract base model that features:
    - UUID as a primary key;
    - `created_at` field with the creation datetime;
    - `updated_at` field with the last updated datetime;
    - Extended `repr` method for better debugging;
    - "Fixed" save method that performs validation.
    """

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Apparently, Django doesn't do a full_clean on every save; only bulk operations
        # Override the save so we can get that full_clean, at a risk of potentially running the validation more than
        # once.
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ("-created_at",)
