from extensions.models import mixins
from django.db.models import Model


class AbstractBaseModel(
    mixins.UUIDPrimaryKeyMixin, mixins.CreatedAtMixin, mixins.UpdatedAtMixin, mixins.ExtendedReprMixin, Model
):
    """
    Abstract base model that features:
    - UUID as a primary key;
    - `created_at` field with the creation datetime;
    - `updated_at` field with the last updated datetime;
    - Extended `repr` method for better debugging.
    """

    class Meta:
        abstract = True
        ordering = ("-created_at",)
