from typing import TYPE_CHECKING, TypeVar
from django.db import models


if TYPE_CHECKING:
    # Prevent circular import
    from extensions.models.mixins import SoftDeleteMixin

    SoftDeleteModel = TypeVar("SoftDeleteModel", bound=SoftDeleteMixin)
else:
    SoftDeleteModel = models.Model


class SoftDeleteManager(models.Manager[SoftDeleteModel]):
    """
    Custom manager for models that implement the `SoftDeleteMixin`. Includes a method `exclude_deleted` to return the
    queryset with the soft deleted models filtered out.
    """

    def exclude_deleted(self) -> models.QuerySet[SoftDeleteModel]:
        """Return this model's queryset, with soft-deleted instances included."""
        return super().get_queryset().filter(is_deleted=False)
