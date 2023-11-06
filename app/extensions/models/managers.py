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
    Custom manager for models that implement the `SoftDeleteMixin`.
    Queries made to this manager will return a queryset with soft-deleted instances filtered out.
    An alternative `include_deleted` method is implemented to return all instances.
    """

    def get_queryset(self) -> models.QuerySet[SoftDeleteModel]:
        """Return this model's queryset. Soft-deleted instances are filtered out."""
        return super().get_queryset().filter(is_deleted=False)

    def include_deleted(self) -> models.QuerySet[SoftDeleteModel]:
        """Return this model's queryset, with soft-deleted instances included."""
        return super().get_queryset()
